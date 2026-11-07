import argparse
import hashlib
import json
import math
import time

from datetime import datetime, timezone
from urllib.request import Request, urlopen

from sdn_port_anomaly_detector import (
    load_samples,
    analyze,
)


ELASTIC_URL = (
    "http://127.0.0.1:9200/"
    "sdnflowguard-events-*/_search"
)

LOGSTASH_URL = "http://127.0.0.1:18080/"


def http_json(url, payload):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        body = response.read()

        if response.status not in (200, 201, 202, 204):
            raise RuntimeError(
                "Unexpected HTTP status: {}".format(
                    response.status
                )
            )

        # Logstash HTTP input may return plain text.
        # A successful HTTP status is sufficient here.
        if url == LOGSTASH_URL:
            return {"accepted": True}

        # Elasticsearch returns JSON and must be parsed.
        return json.loads(body) if body else {}


def make_event(alert, threshold, consecutive):
    identity = {
        "rule": "LAB_HIGH_PPS_TEST_V1",
        "switch": alert["switch_id"],
        "port": alert["port_number"],
        "timestamp": alert["timestamp"],
        "reason": alert["reason"],
        "threshold": threshold,
        "consecutive": consecutive,
    }

    identity_json = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
    )

    alert_key = hashlib.sha256(
        identity_json.encode("utf-8")
    ).hexdigest()

    return {
        "event_id": alert_key,
        "alert_key": alert_key,
        "event_type": "sdn_anomaly_alert",
        "project": "SDNFlowGuard",
        "source": "SDNFlowGuard-AnomalyDetector",
        "telemetry_source": "ONOS",
        "rule_id": "LAB_HIGH_PPS_TEST_V1",
        "reason": alert["reason"],
        "severity": "warning",
        "status": "suspected",
        "test_only": True,
        "detection_mode": "historical_replay",
        "detected_at_utc": alert["timestamp"],
        "published_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "switch_id": alert["switch_id"],
        "port_number": alert["port_number"],
        "rx_pps": alert["rx_pps"],
        "tx_pps": alert["tx_pps"],
        "peak_pps": alert["peak_pps"],
        "threshold_pps": threshold,
        "consecutive_samples": consecutive,
        "message": (
            "Lab test: sustained high packet rate"
        ),
    }


def already_exists(alert_key):
    query = {
        "size": 2,
        "_source": [
            "alert_key",
            "event_type",
        ],
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "alert_key.keyword": alert_key
                        }
                    },
                    {
                        "term": {
                            "alert_key": alert_key
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    }

    result = http_json(ELASTIC_URL, query)

    for hit in result.get("hits", {}).get("hits", []):
        source = hit.get("_source", {})

        if (
            source.get("alert_key") == alert_key
            and source.get("event_type")
            == "sdn_anomaly_alert"
        ):
            return True

    return False


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--minutes",
        type=int,
        default=1440,
    )

    parser.add_argument(
        "--threshold-pps",
        type=float,
        default=4.0,
    )

    parser.add_argument(
        "--consecutive",
        type=int,
        default=2,
    )

    parser.add_argument(
        "--publish",
        action="store_true",
        help="Send test alerts to Logstash",
    )

    args = parser.parse_args()

    if not 1 <= args.minutes <= 10080:
        parser.error("minutes must be 1-10080")

    if (
        not math.isfinite(args.threshold_pps)
        or args.threshold_pps <= 0
        or args.consecutive < 2
    ):
        parser.error("Invalid detection parameters")

    print("=== SDNFLOWGUARD ALERT PUBLISHER ===")

    print(
        "Mode:",
        "PUBLISH TEST ALERTS"
        if args.publish
        else "DRY RUN",
    )

    samples, total = load_samples(args.minutes)

    if total > len(samples):
        raise RuntimeError(
            "Dataset exceeds 500 samples. "
            "Publishing stopped to avoid partial analysis."
        )

    states, alerts = analyze(
        samples,
        args.threshold_pps,
        args.consecutive,
    )

    print("Traffic samples:", len(samples))
    print("Candidate alerts:", len(alerts))
    print("Threshold:", args.threshold_pps, "PPS")

    if not alerts:
        print("No alert candidates found.")
        return

    published = 0
    skipped = 0
    event_keys = []

    for number, alert in enumerate(alerts, start=1):
        event = make_event(
            alert,
            args.threshold_pps,
            args.consecutive,
        )

        event_keys.append(event["alert_key"])

        print(
            "[{}] Switch={} Port={} Peak={} PPS".format(
                number,
                event["switch_id"],
                event["port_number"],
                event["peak_pps"],
            )
        )

        if not args.publish:
            print(
                "  [DRY RUN] No data sent"
            )
            continue

        if already_exists(event["alert_key"]):
            print("  [SKIP] Alert already indexed")
            skipped += 1
            continue

        http_json(LOGSTASH_URL, event)

        print(
            "  [SENT] Logstash accepted {}".format(
                event["alert_key"][:12]
            )
        )

        published += 1

    if args.publish:
        print("\n=== VERIFY ELASTICSEARCH ===")

        verified = 0

        for attempt in range(1, 7):
            time.sleep(2)

            verified = sum(
                already_exists(key)
                for key in event_keys
            )

            if verified == len(event_keys):
                break

        print("New alerts sent:", published)
        print("Existing alerts skipped:", skipped)
        print("Alert IDs found:", verified)
        print("Expected alert IDs:", len(event_keys))

        if verified != len(event_keys):
            raise RuntimeError(
                "Some alerts are not searchable yet. "
                "Check Logstash/Elasticsearch."
            )

        print("SUCCESS - All test alerts verified")

    print("No ONOS flow rules were changed.")
    print("Publisher finished.")


if __name__ == "__main__":
    main()