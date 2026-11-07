import argparse
import base64
import json
import os
import sys
import time
import uuid

from datetime import datetime, timezone
from urllib.request import Request, urlopen


ONOS_URL = "http://127.0.0.1:8181/onos/v1"
LOGSTASH_URL = "http://127.0.0.1:18080/"


def read_onos(endpoint, auth_header):
    request = Request(
        ONOS_URL + endpoint,
        headers={
            "Authorization": auth_header,
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(request, timeout=8) as response:
        return json.load(response)


def collect(auth_header):
    devices = read_onos("/devices", auth_header)["devices"]
    hosts = read_onos("/hosts", auth_header)["hosts"]
    flows = read_onos("/flows", auth_header)["flows"]

    active_switches = [
        device for device in devices
        if device.get("type") == "SWITCH"
        and device.get("available") is True
    ]

    if not active_switches:
        raise RuntimeError(
            "No active ONOS switches. Skipping event."
        )

    event = {
        "event_id": uuid.uuid4().hex,
        "event_type": "sdn_topology_snapshot",
        "project": "SDNFlowGuard",
        "source": "ONOS",
        "collection_method": "ONOS_REST_API",
        "severity": "info",
        "test_only": False,
        "observed_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "device_count": len(devices),
        "available_switches": len(active_switches),
        "host_count": len(hosts),
        "flow_count": len(flows),
        "switch_ids": [
            device.get("id") for device in devices
        ],
        "message": "Automatic ONOS network snapshot",
    }

    return event


def send_logstash(event):
    payload = json.dumps(event).encode("utf-8")

    request = Request(
        LOGSTASH_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        if response.status not in (200, 201, 202, 204):
            raise RuntimeError(
                "Unexpected Logstash HTTP status"
            )


def main():
    if sys.version_info[:3] != (3, 10, 10):
        raise SystemExit(
            "Python 3.10.10 is required."
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()

    if args.interval < 5 or args.count < 0:
        parser.error(
            "interval must be >= 5; count must be >= 0"
        )

    username = os.environ.get("SDNFLOW_ONOS_USER")
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD")

    if not username or not password:
        raise SystemExit(
            "Missing ONOS credentials in environment."
        )

    credentials = base64.b64encode(
        (username + ":" + password).encode("utf-8")
    ).decode("ascii")

    auth_header = "Basic " + credentials

    print("SDNFlowGuard ONOS Collector", flush=True)
    print("Interval:", args.interval, "seconds", flush=True)

    cycle = 0

    while args.count == 0 or cycle < args.count:
        cycle += 1

        try:
            event = collect(auth_header)
            send_logstash(event)

            print(
                "[OK] Cycle={} Switches={} Hosts={} Flows={} ID={}".format(
                    cycle,
                    event["available_switches"],
                    event["host_count"],
                    event["flow_count"],
                    event["event_id"],
                ),
                flush=True,
            )

        except Exception as error:
            print(
                "[ERROR] Cycle={} {}".format(
                    cycle, error
                ),
                flush=True,
            )

        if args.count == 0 or cycle < args.count:
            time.sleep(args.interval)

    print("Collector finished.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCollector stopped safely.")