import argparse
import json
import math
from collections import defaultdict
from datetime import datetime
from urllib.request import Request, urlopen


ELASTIC_URL = (
    "http://127.0.0.1:9200/"
    "sdnflowguard-events-*/_search"
)


def load_samples(minutes):
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
            "sample_seconds"
        ],
        "query": {
            "bool": {
                "filter": [
                    {
                        "match_phrase": {
                            "event_type": "sdn_port_traffic"
                        }
                    },
                    {
                        "range": {
                            "@timestamp": {
                                "gte": f"now-{minutes}m"
                            }
                        }
                    }
                ]
            }
        }
    }

    request = Request(
        ELASTIC_URL,
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=15) as response:
        result = json.load(response)

    total = result["hits"]["total"]["value"]

    samples = [
        hit["_source"]
        for hit in result["hits"]["hits"]
    ]

    samples.reverse()
    return samples, total


def analyze(samples, threshold, consecutive):
    states = defaultdict(
        lambda: {
            "count": 0,
            "peak": 0.0,
            "streak": 0,
            "active": False,
            "last": None
        }
    )

    alerts = []

    for sample in samples:
        switch = sample.get("switch_id")
        port = sample.get("port_number")
        timestamp = sample.get("@timestamp")

        if not switch or port is None or not timestamp:
            continue

        try:
            rx = float(sample.get("rx_pps", 0))
            tx = float(sample.get("tx_pps", 0))
            moment = datetime.strptime(
                timestamp[:19],
                "%Y-%m-%dT%H:%M:%S"
            )
            sample_seconds = float(
                sample.get("sample_seconds") or 15
            )
        except (TypeError, ValueError):
            continue

        if not all(math.isfinite(v) for v in (rx, tx)):
            continue

        if rx < 0 or tx < 0:
            continue

        key = (switch, str(port))
        state = states[key]

        # A long sampling gap breaks a consecutive streak.
        if state["last"] is not None:
            gap = (moment - state["last"]).total_seconds()
            allowed_gap = max(45, sample_seconds * 2.5)

            if gap < 0 or gap > allowed_gap:
                state["streak"] = 0
                state["active"] = False

        state["last"] = moment
        state["count"] += 1

        rate = max(rx, tx)
        state["peak"] = max(state["peak"], rate)

        if rate >= threshold:
            state["streak"] += 1

            if (
                state["streak"] >= consecutive
                and not state["active"]
            ):
                alerts.append({
                    "switch_id": switch,
                    "port_number": str(port),
                    "timestamp": timestamp,
                    "rx_pps": rx,
                    "tx_pps": tx,
                    "peak_pps": rate,
                    "reason": "SUSTAINED_HIGH_PACKET_RATE"
                })

                state["active"] = True
        else:
            state["streak"] = 0
            state["active"] = False

    return states, alerts


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--minutes", type=int, default=1440
    )
    parser.add_argument(
        "--threshold-pps", type=float, default=15.0
    )
    parser.add_argument(
        "--consecutive", type=int, default=2
    )

    args = parser.parse_args()

    if not 1 <= args.minutes <= 10080:
        parser.error("minutes must be 1-10080")

    if (
        not math.isfinite(args.threshold_pps)
        or args.threshold_pps <= 0
        or args.consecutive < 2
    ):
        parser.error(
            "threshold must be positive and consecutive >= 2"
        )

    print("=== SDNFLOWGUARD ANOMALY DETECTOR ===")
    print("Mode: READ ONLY")
    print("Threshold:", args.threshold_pps, "PPS")
    print("Consecutive samples:", args.consecutive)

    samples, total = load_samples(args.minutes)

    print("Samples analyzed:", len(samples))

    if total > len(samples):
        print(
            "NOTICE: Only the 500 latest samples "
            "were analyzed."
        )

    states, alerts = analyze(
        samples,
        args.threshold_pps,
        args.consecutive
    )

    print("\n=== PORT ANALYSIS ===")

    for (switch, port), state in sorted(states.items()):
        print(
            "Switch={} Port={} Samples={} "
            "Peak={:.3f} PPS".format(
                switch,
                port,
                state["count"],
                state["peak"]
            )
        )

    print("\n=== DETECTION RESULT ===")

    if not alerts:
        print(
            "NORMAL - No sustained high-packet-rate "
            "candidate detected."
        )
    else:
        for alert in alerts:
            print(
                "[SUSPECTED] {}".format(
                    json.dumps(alert, ensure_ascii=False)
                )
            )

    print("Alert candidates:", len(alerts))
    print("No ONOS flow rules were changed.")
    print("Detector finished.")


if __name__ == "__main__":
    main()