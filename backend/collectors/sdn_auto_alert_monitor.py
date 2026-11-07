import argparse
import hashlib
import json
import math
import sys
import time

from datetime import datetime, timezone
from urllib.request import Request, urlopen

from sdn_alert_publisher import (
    already_exists,
    http_json,
    LOGSTASH_URL,
)


ELASTIC_URL = (
    "http://127.0.0.1:9200/"
    "sdnflowguard-events-*/_search"
)

RULE_ID = "LAB_HIGH_PPS_AUTO_V1"


def fetch_samples(minutes):
    query = {
        "size": 500,
        "track_total_hits": True,
        "sort": [
            {"@timestamp": {"order": "desc"}}
        ],
        "_source": [
            "@timestamp",
            "event_id",
            "switch_id",
            "port_number",
            "rx_pps",
            "tx_pps",
            "sample_seconds",
        ],
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "event_type.keyword":
                            "sdn_port_traffic"
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{minutes}m"
                            }
                        }
                    },
                ]
            }
        },
    }

    request = Request(
        ELASTIC_URL,
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=12) as response:
        result = json.load(response)

    hits = result.get("hits", {})
    total = hits.get("total", {}).get("value", 0)
    documents = hits.get("hits", [])

    if total > len(documents):
        raise RuntimeError(
            "More than 500 samples in lookback. "
            "Partial processing is disabled."
        )

    return list(reversed(documents))


def identity(hit):
    return "{}:{}".format(
        hit.get("_index", ""),
        hit.get("_id", ""),
    )


def valid_sample(hit):
    item = hit.get("_source") or {}

    switch = item.get("switch_id")
    port = item.get("port_number")
    stamp = item.get("@timestamp")

    if not switch or port is None or not stamp:
        return None

    try:
        rx = float(item["rx_pps"])
        tx = float(item["tx_pps"])
        interval = float(
            item.get("sample_seconds") or 10.0
        )

        when = datetime.strptime(
            stamp[:19],
            "%Y-%m-%dT%H:%M:%S",
        ).replace(tzinfo=timezone.utc)

    except (KeyError, TypeError, ValueError):
        return None

    numbers = (rx, tx, interval)

    if not all(math.isfinite(n) for n in numbers):
        return None

    if rx < 0 or tx < 0 or interval <= 0:
        return None

    return (
        str(switch),
        str(port),
        stamp,
        when,
        rx,
        tx,
        interval,
    )


def make_alert(hit, sample, threshold, consecutive):
    switch, port, stamp, _, rx, tx, _ = sample

    source_id = (
        (hit.get("_source") or {}).get("event_id")
        or identity(hit)
    )

    token = json.dumps(
        [
            RULE_ID,
            source_id,
            switch,
            port,
            threshold,
            consecutive,
        ],
        separators=(",", ":"),
    )

    key = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    return {
        "event_id": key,
        "alert_key": key,
        "event_type": "sdn_anomaly_alert",
        "project": "SDNFlowGuard",
        "source": "SDNFlowGuard-AutoMonitor",
        "telemetry_source": "ONOS",
        "rule_id": RULE_ID,
        "reason": "SUSTAINED_HIGH_PACKET_RATE",
        "severity": "warning",
        "status": "suspected",
        "test_only": True,
        "detection_mode": "live_lab_monitor",
        "detected_at_utc": stamp,
        "published_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "switch_id": switch,
        "port_number": port,
        "rx_pps": rx,
        "tx_pps": tx,
        "peak_pps": max(rx, tx),
        "threshold_pps": threshold,
        "consecutive_samples": consecutive,
        "source_event_id": source_id,
        "message": (
            "Lab monitor: sustained high packet rate"
        ),
    }


def main():
    if sys.version_info[:3] != (3, 10, 10):
        raise SystemExit(
            "Python 3.10.10 required"
        )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--poll-seconds", type=int, default=5
    )
    parser.add_argument(
        "--cycles", type=int, default=24
    )
    parser.add_argument(
        "--lookback-minutes", type=int, default=5
    )
    parser.add_argument(
        "--threshold-pps", type=float, default=15.0
    )
    parser.add_argument(
        "--consecutive", type=int, default=2
    )
    parser.add_argument(
        "--publish-test-alerts",
        action="store_true",
    )

    args = parser.parse_args()

    if (
        args.poll_seconds < 3
        or args.cycles < 0
        or not 1 <= args.lookback_minutes <= 60
    ):
        parser.error("Invalid polling parameters")

    if (
        not math.isfinite(args.threshold_pps)
        or args.threshold_pps <= 0
        or args.consecutive < 2
    ):
        parser.error("Invalid detection parameters")

    initial = fetch_samples(args.lookback_minutes)

    # Ignore all historical records on startup.
    seen = {
        identity(hit)
        for hit in initial
    }

    states = {}
    candidate_count = 0

    print(
        "=== SDNFLOWGUARD AUTO ALERT MONITOR ===",
        flush=True,
    )

    print(
        "Mode:",
        "PUBLISH TEST ALERTS"
        if args.publish_test_alerts
        else "DRY RUN",
        flush=True,
    )

    print(
        "Existing samples ignored:",
        len(seen),
        flush=True,
    )

    print(
        "Threshold:",
        args.threshold_pps,
        "PPS",
        flush=True,
    )

    print(
        "Required consecutive samples:",
        args.consecutive,
        flush=True,
    )

    cycle = 0

    while args.cycles == 0 or cycle < args.cycles:
        cycle += 1

        try:
            hits = fetch_samples(
                args.lookback_minutes
            )

            new_count = 0

            for hit in hits:
                doc_id = identity(hit)

                if doc_id in seen:
                    continue

                sample = valid_sample(hit)
                seen.add(doc_id)

                if sample is None:
                    continue

                new_count += 1

                (
                    switch,
                    port,
                    stamp,
                    when,
                    rx,
                    tx,
                    interval,
                ) = sample

                key = (switch, port)

                state = states.setdefault(
                    key,
                    {
                        "streak": 0,
                        "active": False,
                        "last": None,
                    },
                )

                if state["last"] is not None:
                    gap = (
                        when - state["last"]
                    ).total_seconds()

                    if (
                        gap <= 0
                        or gap > max(
                            45.0,
                            interval * 2.5,
                        )
                    ):
                        state["streak"] = 0
                        state["active"] = False

                state["last"] = when

                if max(rx, tx) >= args.threshold_pps:
                    state["streak"] += 1

                    if (
                        state["streak"] >= args.consecutive
                        and not state["active"]
                    ):
                        alert = make_alert(
                            hit,
                            sample,
                            args.threshold_pps,
                            args.consecutive,
                        )

                        print(
                            "[SUSPECTED TEST] "
                            "Switch={} Port={} "
                            "Peak={:.3f} PPS".format(
                                switch,
                                port,
                                alert["peak_pps"],
                            ),
                            flush=True,
                        )

                        if args.publish_test_alerts:
                            if already_exists(
                                alert["alert_key"]
                            ):
                                print(
                                    "  [SKIP] Already indexed",
                                    flush=True,
                                )
                            else:
                                http_json(
                                    LOGSTASH_URL,
                                    alert,
                                )

                                print(
                                    "  [SENT] Logstash accepted test alert",
                                    flush=True,
                                )
                        else:
                            print(
                                "  [DRY RUN] No alert sent",
                                flush=True,
                            )

                        candidate_count += 1
                        state["active"] = True

                else:
                    state["streak"] = 0
                    state["active"] = False

            # Keep memory bounded to recent documents.
            recent_ids = {
                identity(hit)
                for hit in hits
            }

            seen.intersection_update(recent_ids)

            print(
                "[POLL] Cycle={} "
                "New samples={} "
                "Candidates={}".format(
                    cycle,
                    new_count,
                    candidate_count,
                ),
                flush=True,
            )

        except Exception as error:
            print(
                "[ERROR] Poll {}: {}".format(
                    cycle,
                    error,
                ),
                flush=True,
            )

            raise SystemExit(1) from error

        if args.cycles == 0 or cycle < args.cycles:
            time.sleep(args.poll_seconds)

    print(
        "Candidate alerts this run:",
        candidate_count,
        flush=True,
    )

    print(
        "No ONOS flow rules were changed.",
        flush=True,
    )

    print(
        "Auto monitor finished.",
        flush=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\nAuto monitor stopped safely."
        )