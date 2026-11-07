import argparse
import base64
import json
import os
import sys
import time
import uuid

from datetime import datetime, timezone
from urllib.request import Request, urlopen


ONOS_URL = "http://127.0.0.1:8181/onos/v1/statistics/ports"
LOGSTASH_URL = "http://127.0.0.1:18080/"

COUNTERS = (
    "bytesReceived",
    "bytesSent",
    "packetsReceived",
    "packetsSent",
)


def read_statistics(auth):
    request = Request(
        ONOS_URL,
        headers={
            "Authorization": auth,
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(request, timeout=10) as response:
        data = json.load(response)

    result = {}

    for device in data.get("statistics", []):
        device_id = device.get("device")

        if not device_id:
            continue

        for port in device.get("ports", []):
            port_id = str(port.get("port", ""))

            if not port_id.isdecimal():
                continue

            # Skip reserved OpenFlow ports.
            if int(port_id) >= 0xFFFFFF00:
                continue

            try:
                counters = {
                    name: int(port[name])
                    for name in COUNTERS
                }
            except (KeyError, TypeError, ValueError):
                continue

            if any(value < 0 for value in counters.values()):
                continue

            result[(device_id, port_id)] = counters

    return result


def send_event(event):
    body = json.dumps(event).encode("utf-8")

    request = Request(
        LOGSTASH_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        if response.status not in (200, 201, 202, 204):
            raise RuntimeError(
                "Logstash rejected the event"
            )


def main():
    if sys.version_info[:3] != (3, 10, 10):
        raise SystemExit("Python 3.10.10 required")

    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()

    if args.interval < 5 or args.count < 2:
        parser.error(
            "interval >= 5 and count >= 2 required"
        )

    user = os.environ.get("SDNFLOW_ONOS_USER")
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD")

    if not user or not password:
        raise SystemExit("ONOS credentials missing")

    encoded = base64.b64encode(
        f"{user}:{password}".encode("utf-8")
    ).decode("ascii")

    auth = "Basic " + encoded

    previous = None
    previous_time = None
    sent = 0

    print("SDNFlowGuard Port Traffic Collector")
    print("Interval:", args.interval, "seconds")

    for cycle in range(1, args.count + 1):
        try:
            current = read_statistics(auth)
            now = time.monotonic()

            if not current:
                raise RuntimeError(
                    "ONOS returned no valid port counters"
                )

            if previous is None:
                print(
                    "[BASELINE] Cycle={} Ports={}".format(
                        cycle, len(current)
                    ),
                    flush=True,
                )

            else:
                seconds = now - previous_time
                cycle_events = 0

                for key, counters in current.items():
                    old = previous.get(key)

                    if old is None:
                        continue

                    if any(
                        counters[name] < old[name]
                        for name in COUNTERS
                    ):
                        print(
                            "[RESET] Device={} Port={}".format(
                                key[0], key[1]
                            )
                        )
                        continue

                    rx_delta = (
                        counters["bytesReceived"]
                        - old["bytesReceived"]
                    )
                    tx_delta = (
                        counters["bytesSent"]
                        - old["bytesSent"]
                    )

                    rx_packets_delta = (
                        counters["packetsReceived"]
                        - old["packetsReceived"]
                    )
                    tx_packets_delta = (
                        counters["packetsSent"]
                        - old["packetsSent"]
                    )

                    event = {
                        "event_id": uuid.uuid4().hex,
                        "event_type": "sdn_port_traffic",
                        "project": "SDNFlowGuard",
                        "source": "ONOS",
                        "collection_method": "ONOS_REST_API",
                        "test_only": False,
                        "severity": "info",
                        "observed_at_utc": datetime.now(
                            timezone.utc
                        ).isoformat(),
                        "switch_id": key[0],
                        "port_number": key[1],
                        "sample_seconds": round(seconds, 3),
                        "rx_bytes": counters["bytesReceived"],
                        "tx_bytes": counters["bytesSent"],
                        "rx_packets": counters["packetsReceived"],
                        "tx_packets": counters["packetsSent"],
                        "rx_mbps": round(
                            rx_delta * 8 / seconds / 1_000_000,
                            6,
                        ),
                        "tx_mbps": round(
                            tx_delta * 8 / seconds / 1_000_000,
                            6,
                        ),
                        "rx_pps": round(
                            rx_packets_delta / seconds, 3
                        ),
                        "tx_pps": round(
                            tx_packets_delta / seconds, 3
                        ),
                        "message": "ONOS port traffic sample",
                    }

                    send_event(event)
                    cycle_events += 1
                    sent += 1

                    print(
                        "[OK] Cycle={} Port={} "
                        "RX={} Mbps TX={} Mbps".format(
                            cycle,
                            key[1],
                            event["rx_mbps"],
                            event["tx_mbps"],
                        ),
                        flush=True,
                    )

                print(
                    "Cycle {}: {} events sent".format(
                        cycle, cycle_events
                    )
                )

            previous = current
            previous_time = now

        except Exception as error:
            print(
                "[ERROR] Cycle={} {}".format(
                    cycle, error
                ),
                flush=True,
            )
            previous = None
            previous_time = None

        if cycle < args.count:
            time.sleep(args.interval)

    print("Total events sent:", sent)
    print("Port collector finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPort collector stopped safely.")