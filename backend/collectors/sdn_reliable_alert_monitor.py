import argparse
import json
import math
import os
import time

from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

try:
    import msvcrt

    def lock_handle(handle):
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)

    def unlock_handle(handle):
        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
except ImportError:
    import fcntl

    def lock_handle(handle):
        handle.seek(0)
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def unlock_handle(handle):
        try:
            handle.seek(0)
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass

from sdn_auto_alert_monitor import valid_sample, make_alert
from sdn_alert_publisher import (
    already_exists,
    http_json,
    LOGSTASH_URL,
)


ELASTIC_URL = (
    "http://127.0.0.1:9200/"
    "sdnflowguard-events-*/_search"
)

STATE_DIR = Path(__file__).resolve().parent / "state"

SORT_ASC = [
    {
        "@timestamp": {
            "order": "asc",
            "format": "strict_date_optional_time_nanos",
        }
    },
    {"event_id.keyword": {"order": "asc"}},
]


def search_elastic(query):
    request = Request(
        ELASTIC_URL,
        data=json.dumps(query).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        return json.load(response)


def base_filter(days):
    return {
        "bool": {
            "filter": [
                {
                    "term": {
                        "event_type.keyword": "sdn_port_traffic"
                    }
                },
                {
                    "exists": {
                        "field": "event_id.keyword"
                    }
                },
                {
                    "range": {
                        "@timestamp": {
                            "gte": f"now-{days}d"
                        }
                    }
                },
            ]
        }
    }


def fetch_page(days, cursor, size=100):
    query = {
        "size": size,
        "sort": SORT_ASC,
        "query": base_filter(days),
    }

    if cursor is not None:
        query["search_after"] = cursor

    result = search_elastic(query)

    return result.get("hits", {}).get("hits", [])


def latest_cursor(days):
    query = {
        "size": 1,
        "sort": [
            {
                "@timestamp": {
                    "order": "desc",
                    "format": "strict_date_optional_time_nanos",
                }
            },
            {"event_id.keyword": {"order": "desc"}},
        ],
        "query": base_filter(days),
    }

    result = search_elastic(query)
    hits = result.get("hits", {}).get("hits", [])

    return hits[0]["sort"] if hits else None


def save_checkpoint(path, state):
    temp = path.with_suffix(".tmp")

    with open(temp, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())

    os.replace(temp, path)


def load_checkpoint(path, args):
    if path.exists():
        with open(path, encoding="utf-8") as handle:
            state = json.load(handle)

        if (
            state.get("version") != 1
            or state.get("threshold_pps") != args.threshold_pps
            or state.get("consecutive") != args.consecutive
        ):
            raise RuntimeError(
                "Checkpoint configuration mismatch. "
                "Existing state was preserved."
            )

        print("[RESUME] Existing checkpoint loaded")
        return state

    state = {
        "version": 1,
        "threshold_pps": args.threshold_pps,
        "consecutive": args.consecutive,
        "cursor": latest_cursor(args.lookback_days),
        "ports": {},
        "updated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    save_checkpoint(path, state)
    print("[BOOTSTRAP] Current Elasticsearch position saved")
    print("Historical records will not generate new alerts.")

    return state


def process_hit(hit, state, args):
    sample = valid_sample(hit)

    if sample is None:
        return False

    (
        switch,
        port,
        stamp,
        when,
        rx,
        tx,
        interval,
    ) = sample

    key = switch + "|" + port

    port_state = state["ports"].get(
        key,
        {
            "streak": 0,
            "active": False,
            "last": None,
        },
    )

    last = port_state.get("last")

    if last is not None:
        previous = datetime.fromisoformat(last)
        gap = (when - previous).total_seconds()

        if gap <= 0 or gap > max(45.0, interval * 2.5):
            port_state["streak"] = 0
            port_state["active"] = False

    rate = max(rx, tx)
    candidate = False

    if rate >= args.threshold_pps:
        port_state["streak"] += 1

        if (
            port_state["streak"] >= args.consecutive
            and not port_state["active"]
        ):
            alert = make_alert(
                hit,
                sample,
                args.threshold_pps,
                args.consecutive,
            )

            print(
                "[CANDIDATE] Switch={} Port={} "
                "Peak={:.3f} PPS".format(
                    switch,
                    port,
                    rate,
                ),
                flush=True,
            )

            if args.publish_test_alerts:
                if already_exists(alert["alert_key"]):
                    print("[SKIP] Alert already indexed")
                else:
                    http_json(LOGSTASH_URL, alert)

                    # Do not advance the checkpoint until
                    # Elasticsearch confirms the alert.
                    confirmed = False

                    for _ in range(10):
                        time.sleep(1)

                        if already_exists(alert["alert_key"]):
                            confirmed = True
                            break

                    if not confirmed:
                        raise RuntimeError(
                            "Alert not indexed yet. "
                            "Checkpoint was not advanced."
                        )

                    print("[SENT] Alert indexed successfully")
            else:
                print("[DRY RUN] No alert sent")

            port_state["active"] = True
            candidate = True
    else:
        port_state["streak"] = 0
        port_state["active"] = False

    port_state["last"] = when.isoformat()
    state["ports"][key] = port_state

    return candidate


def acquire_lock(path):
    handle = open(path, "a+b")

    handle.seek(0, os.SEEK_END)

    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()

    handle.seek(0)

    try:
        lock_handle(handle)
    except OSError:
        handle.close()
        raise RuntimeError(
            "Another monitor with this configuration "
            "is already running."
        )

    return handle


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--poll-seconds", type=int, default=5
    )
    parser.add_argument(
        "--cycles", type=int, default=3
    )
    parser.add_argument(
        "--lookback-days", type=int, default=7
    )
    parser.add_argument(
        "--threshold-pps", type=float, default=4.0
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
        or not 1 <= args.lookback_days <= 7
        or not math.isfinite(args.threshold_pps)
        or args.threshold_pps <= 0
        or args.consecutive < 2
    ):
        parser.error("Invalid monitor parameters")

    STATE_DIR.mkdir(parents=True, exist_ok=True)

    mode = (
        "publish"
        if args.publish_test_alerts
        else "dry"
    )

    threshold_tag = format(
        args.threshold_pps, "g"
    ).replace(".", "p")

    name = (
        f"auto_{mode}_t{threshold_tag}"
        f"_c{args.consecutive}"
    )

    state_path = STATE_DIR / (name + ".json")
    lock_path = STATE_DIR / (name + ".lock")

    lock_handle = acquire_lock(lock_path)

    try:
        state = load_checkpoint(
            state_path,
            args,
        )

        print("=== RELIABLE SDN ALERT MONITOR ===")
        print("Mode:", mode.upper())
        print("Checkpoint:", state_path)
        print("Threshold:", args.threshold_pps, "PPS")

        cycle = 0
        candidates = 0

        while args.cycles == 0 or cycle < args.cycles:
            cycle += 1

            processed = 0
            pages = 0

            while pages < 30:
                hits = fetch_page(
                    args.lookback_days,
                    state["cursor"],
                )

                if not hits:
                    break

                pages += 1

                for hit in hits:
                    if process_hit(hit, state, args):
                        candidates += 1

                    state["cursor"] = hit["sort"]
                    state["updated_at_utc"] = datetime.now(
                        timezone.utc
                    ).isoformat()

                    save_checkpoint(
                        state_path,
                        state,
                    )

                    processed += 1

                if len(hits) < 100:
                    break

            print(
                "[POLL] Cycle={} New={} "
                "Candidates={}".format(
                    cycle,
                    processed,
                    candidates,
                ),
                flush=True,
            )

            if args.cycles == 0 or cycle < args.cycles:
                time.sleep(args.poll_seconds)

        print("Candidate alerts:", candidates)
        print("Checkpoint saved:", state_path)
        print("No ONOS flow rules were changed.")
        print("Reliable monitor finished.")

    finally:
        try:
            unlock_handle(lock_handle)
        finally:
            lock_handle.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitor stopped safely.")