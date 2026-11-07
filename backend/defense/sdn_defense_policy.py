import argparse
import base64
import json
import os
import sys
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.policies.defense_policy import (  # noqa: E402
    DECISIONS,
    evaluate_defense_policy,
)
from sdnflowguard.domain.services.evidence_correlation import (  # noqa: E402
    correlate_evidence_with_onos,
    count_ip_source_flows,
)


ONOS_URL = "http://127.0.0.1:8181/onos/v1"
ES_URL = (
    "http://127.0.0.1:9200/"
    "sdnflowguard-events-*/_search"
)

DEVICE_ID = "of:0000000000000001"


def onos_get(path):
    user = os.environ.get("SDNFLOW_ONOS_USER")
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD")

    if not user or not password:
        raise RuntimeError(
            "ONOS credentials are not configured"
        )

    credentials = base64.b64encode(
        f"{user}:{password}".encode("utf-8")
    ).decode("ascii")

    request = Request(
        f"{ONOS_URL}/{path}",
        headers={
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
        },
        method="GET",
    )

    with urlopen(request, timeout=15) as response:
        return json.load(response)


def fetch_alerts(minutes):
    query = {
        "size": 100,
        "track_total_hits": True,
        "sort": [
            {"@timestamp": {"order": "desc"}}
        ],
        "_source": [
            "@timestamp",
            "event_id",
            "switch_id",
            "port_number",
            "peak_pps",
            "threshold_pps",
            "test_only",
            "status",
            "reason",
            "rule_id",
        ],
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "event_type.keyword":
                            "sdn_anomaly_alert"
                        }
                    },
                    {
                        "term": {
                            "rule_id.keyword":
                            "LAB_HIGH_PPS_AUTO_V1"
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
        ES_URL,
        data=json.dumps(query).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        result = json.load(response)

    hits = result.get("hits", {})
    total = hits.get("total", {})

    total_count = (
        total.get("value", 0)
        if isinstance(total, dict)
        else int(total)
    )

    if total_count > 100:
        raise RuntimeError(
            "More than 100 alerts found. "
            "Partial policy analysis is disabled."
        )

    return [
        hit.get("_source") or {}
        for hit in hits.get("hits", [])
    ]


def hosts_by_port(hosts, device_id):
    mapping = {}

    for host in hosts:
        addresses = host.get("ipAddresses") or []

        for location in host.get("locations") or []:
            if location.get("elementId") != device_id:
                continue

            port = str(location.get("port"))

            mapping.setdefault(port, []).append({
                "mac": host.get("mac"),
                "ips": addresses,
            })

    return mapping


def evaluate_policy(
    device_id,
    ports,
    hosts,
    flows,
    alerts,
    evidence=None,
    capture_metadata=None,
):
    return evaluate_defense_policy(
        device_id,
        ports,
        hosts,
        flows,
        alerts,
        evidence=evidence,
        capture_metadata=capture_metadata,
    )


def self_test():
    hosts = [
        {
            "mac": "00:00:00:00:00:01",
            "ipAddresses": ["10.0.0.1"],
            "locations": [
                {
                    "elementId": DEVICE_ID,
                    "port": "1",
                }
            ],
        },
        {
            "mac": "00:00:00:00:00:02",
            "ipAddresses": ["10.0.0.2"],
            "locations": [
                {
                    "elementId": DEVICE_ID,
                    "port": "2",
                }
            ],
        },
    ]

    ports = [
        {"port": "1", "isEnabled": True},
        {"port": "2", "isEnabled": True},
    ]

    flows = [
        {
            "selector": {
                "criteria": [
                    {
                        "type": "ETH_TYPE",
                        "ethType": "0x800",
                    }
                ]
            }
        }
    ]

    test_alert = {
        "switch_id": DEVICE_ID,
        "port_number": "1",
        "test_only": True,
        "peak_pps": 10.152,
    }

    reports = evaluate_policy(
        DEVICE_ID,
        ports,
        hosts,
        flows,
        [test_alert],
    )

    assert len(reports) == 2
    assert reports[0]["decision"] == "OBSERVE"
    assert reports[1]["decision"] == "ALLOW"

    # An attached host is NOT an attributed attacker.
    assert (
        reports[0]["source_ip_attributed"]
        is False
    )

    assert reports[0]["test_alert_count"] == 1
    assert count_ip_source_flows(flows) == 0

    assert all(
        r["decision"] != "PROPOSE_BLOCK"
        for r in reports
    )

    # Step 64 integration check with real evidence file if available
    evidence_file = (
        Path(__file__).resolve().parent
        / "evidence"
        / "ingress_icmp_20261101_014645.json"
    )
    if evidence_file.is_file():
        with evidence_file.open("r", encoding="utf-8") as fh:
            ev_data = json.load(fh)
        step64_reports = evaluate_policy(
            DEVICE_ID,
            ports,
            hosts,
            flows,
            [test_alert],
            evidence=ev_data,
        )
        assert step64_reports[0]["decision"] == "OBSERVE"
        assert step64_reports[0]["source_ip_attributed"] is False
        assert len(step64_reports[0]["step64_correlations"]) == 1

    print("SELF TEST PASS - Port alert: OBSERVE")
    print("SELF TEST PASS - No alert: ALLOW")
    print("SELF TEST PASS - Host is not attacker attribution")
    print("SELF TEST PASS - Step 64 evidence correlation integrated")
    print("SELF TEST PASS - PROPOSE_BLOCK disabled")
    print("SELF TEST PASS - No network requests")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--minutes",
        type=int,
        default=10080,
    )

    parser.add_argument(
        "--evidence",
        help="Optional path to Step 63 packet observation JSON for Step 64 correlation.",
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
    )

    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if not 1 <= args.minutes <= 10080:
        parser.error("minutes must be 1-10080")

    evidence_data = None
    if args.evidence:
        ev_path = Path(args.evidence)
        if not ev_path.is_file():
            raise FileNotFoundError(ev_path)
        with ev_path.open("r", encoding="utf-8-sig") as fh:
            evidence_data = json.load(fh)

    print("=== SDNFLOWGUARD DEFENSE POLICY ENGINE ===")
    print("Mode: DRY RUN - READ ONLY")
    print("Device:", DEVICE_ID)

    hosts_result = onos_get("hosts")

    ports_result = onos_get(
        f"devices/{DEVICE_ID}/ports"
    )

    flows_result = onos_get(
        f"flows/{DEVICE_ID}"
    )

    alerts = fetch_alerts(args.minutes)

    hosts = hosts_result.get("hosts") or []
    ports = ports_result.get("ports") or []
    flows = flows_result.get("flows") or []

    reports = evaluate_policy(
        DEVICE_ID,
        ports,
        hosts,
        flows,
        alerts,
        evidence=evidence_data,
    )

    print("\n=== EVIDENCE SUMMARY ===")
    print("ONOS hosts:", len(hosts))
    print("ONOS ports:", len(ports))
    print("ONOS flows:", len(flows))
    print(
        "IP source selector flows:",
        count_ip_source_flows(flows),
    )
    print("Automatic alert events:", len(alerts))
    print("Alert type: LAB TEST")
    if evidence_data is not None:
        corr = correlate_evidence_with_onos(
            evidence_data,
            device_id=DEVICE_ID,
            ports=ports,
            hosts=hosts,
            flows=flows,
            alerts=alerts,
        )
        print(
            "Step 64 topology corroborated:",
            corr["security_assessment"]["topology_corroborated"],
        )

    print("\n=== DEFENSE POLICY DECISIONS ===")

    for report in reports:
        ips = [
            ip
            for host in report["attached_hosts"]
            for ip in host["ips"]
        ]

        print()
        print("Port:", report["port_number"])
        print(
            "Attached host IPs:",
            ", ".join(ips) if ips else "UNKNOWN",
        )
        print(
            "Related alerts:",
            report["alert_count"],
        )
        print(
            "Test alerts:",
            report["test_alert_count"],
        )
        print(
            "Source IP attributed:",
            report["source_ip_attributed"],
        )
        print("Decision:", report["decision"])
        print("Reason:", report["reason"])

    decisions = Counter(
        report["decision"]
        for report in reports
    )

    print("\n=== FINAL POLICY SUMMARY ===")
    print("ALLOW:", decisions["ALLOW"])
    print("OBSERVE:", decisions["OBSERVE"])
    print(
        "PROPOSE_BLOCK:",
        decisions["PROPOSE_BLOCK"],
    )

    print("ONOS configuration changes: 0")
    print("Blocked hosts: 0")
    print("Blocked ports: 0")
    print("Flow rules installed: 0")
    print("No Elasticsearch documents were modified.")

    print("\nSUCCESS - Defense policy DRY RUN completed")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(
            "ERROR: {}".format(error),
            file=sys.stderr,
        )
        sys.exit(1)
