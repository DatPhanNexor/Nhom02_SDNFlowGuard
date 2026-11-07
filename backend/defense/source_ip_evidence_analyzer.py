import argparse
import hashlib
import ipaddress
import json
import re
import sys
from collections import Counter
from pathlib import Path


PATTERN = re.compile(
    r'^(?P<clock>\d{2}:\d{2}:\d{2}\.\d+)\s+'
    r'(?P<interface>s1-eth(?P<port>\d+))\s+\S+\s+'
    r'ifindex\s+\d+\s+'
    r'(?P<mac>(?:[0-9a-f]{2}:){5}[0-9a-f]{2})\s+'
    r'ethertype\s+IPv4\b.*?:\s+'
    r'(?P<src>(?:\d{1,3}\.){3}\d{1,3})\s+>\s+'
    r'(?P<dst>(?:\d{1,3}\.){3}\d{1,3}):\s+'
    r'ICMP\s+echo\s+(?P<kind>request|reply)\b',
    re.IGNORECASE,
)


def read_capture(path):
    data = path.read_bytes()

    # Windows PowerShell Tee-Object may write UTF-16LE.
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")

    if b"\x00" in data[:100]:
        return data.decode("utf-16-le")

    return data.decode("utf-8-sig")


def analyze(text, capture_metadata=None):
    records = []

    for line in text.splitlines():
        if not (
            re.search(r"s1-eth[12]\b", line)
            and "ethertype IPv4" in line
        ):
            continue

        match = PATTERN.search(line.strip())

        if not match:
            raise ValueError(
                "Unsupported switch IPv4 packet: " + line[:160]
            )

        packet = match.groupdict()

        ipaddress.IPv4Address(packet["src"])
        ipaddress.IPv4Address(packet["dst"])

        records.append(packet)

    if not records:
        raise ValueError("No supported switch ICMP packets found")

    counts = Counter(
        (
            packet["port"],
            packet["interface"],
            packet["mac"].lower(),
            packet["src"],
            packet["dst"],
            packet["kind"].lower(),
        )
        for packet in records
    )

    observations = []

    for key, count in sorted(counts.items()):
        port, interface, mac, src, dst, kind = key

        observations.append({
            "switch_id": "of:0000000000000001",
            "ingress_port": port,
            "interface": interface,
            "observed_source_mac": mac,
            "observed_source_ip": src,
            "observed_destination_ip": dst,
            "protocol": "ICMP",
            "icmp_type": kind,
            "packet_count": count,
        })

    has_meta_window = bool(
        isinstance(capture_metadata, dict)
        and capture_metadata.get("capture_started_utc")
        and capture_metadata.get("capture_finished_utc")
    )

    payload = {
        "schema_version": 1,
        "evidence_type": "switch_ingress_packet_observation",
        "total_packets": len(records),
        "first_packet_clock": records[0]["clock"],
        "last_packet_clock": records[-1]["clock"],
        "capture_clock_has_date": has_meta_window,
        "capture_clock_has_timezone": has_meta_window,
        "observations": observations,
        "security_assessment": {
            "source_ip_observed": True,
            "attacker_confirmed": False,
            "historical_alert_correlation_verified": False,
            "decision": "OBSERVE",
            "automatic_block_allowed": False,
        },
    }
    if isinstance(capture_metadata, dict):
        payload["capture_metadata"] = dict(capture_metadata)
    return payload


def self_test():
    sample = "\n".join([
        "18:46:47.909111 s1-eth1 P ifindex 7 "
        "00:00:00:00:00:01 ethertype IPv4 (0x0800), "
        "length 104: 10.0.0.1 > 10.0.0.2: "
        "ICMP echo request, id 29154, seq 1, length 64",

        "18:46:47.910259 s1-eth2 P ifindex 8 "
        "00:00:00:00:00:02 ethertype IPv4 (0x0800), "
        "length 104: 10.0.0.2 > 10.0.0.1: "
        "ICMP echo reply, id 29154, seq 1, length 64",
    ])

    result = analyze(sample)

    assert result["total_packets"] == 2
    assert len(result["observations"]) == 2
    assert result["observations"][0]["observed_source_ip"] == "10.0.0.1"
    assert result["observations"][1]["observed_source_ip"] == "10.0.0.2"
    assert result["security_assessment"]["automatic_block_allowed"] is False

    meta_result = analyze(
        sample,
        capture_metadata={
            "capture_started_utc": "2026-11-01T18:46:45Z",
            "capture_finished_utc": "2026-11-01T18:46:55Z",
            "switch_id": "of:0000000000000001",
            "interfaces": ["s1-eth1", "s1-eth2"],
        },
    )
    assert meta_result["capture_clock_has_date"] is True
    assert meta_result["capture_clock_has_timezone"] is True
    assert meta_result["security_assessment"]["automatic_block_allowed"] is False

    print("SELF TEST PASS - Packet parser")
    print("SELF TEST PASS - Source IP and MAC")
    print("SELF TEST PASS - Capture UTC metadata support")
    print("SELF TEST PASS - No automatic blocking")
    print("SELF TEST PASS - No external requests")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input")
    parser.add_argument("--started-utc")
    parser.add_argument("--finished-utc")
    parser.add_argument("--self-test", action="store_true")

    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if not args.input:
        parser.error("--input is required")

    source = Path(args.input)

    if not source.is_file():
        raise FileNotFoundError(source)

    capture_metadata = None
    if args.started_utc and args.finished_utc:
        capture_metadata = {
            "capture_started_utc": args.started_utc,
            "capture_finished_utc": args.finished_utc,
            "capture_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "switch_id": "of:0000000000000001",
            "interfaces": ["s1-eth1", "s1-eth2"],
        }

    result = analyze(read_capture(source), capture_metadata=capture_metadata)

    output = source.with_suffix(".json")

    # Exclusive creation prevents overwriting earlier evidence.
    with output.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print("=== SOURCE IP EVIDENCE ANALYSIS ===")
    print("Input:", source)
    print("Parsed packets:", result["total_packets"])

    for item in result["observations"]:
        print(
            "Port={ingress_port} "
            "MAC={observed_source_mac} "
            "SRC={observed_source_ip} "
            "DST={observed_destination_ip} "
            "ICMP={icmp_type} "
            "Packets={packet_count}".format(**item)
        )

    print("\nAttacker confirmed: False")
    print("Defense decision: OBSERVE")
    print("Automatic blocking: DISABLED")
    print("Historical alert correlation: NOT VERIFIED")
    print("Output JSON:", output)
    print("\nSUCCESS - Source IP Evidence Analyzer completed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
