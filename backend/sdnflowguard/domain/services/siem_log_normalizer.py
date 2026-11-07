"""SIEM Log Normalizer & Multi-Source Capability Evaluator.

Evaluates and normalizes security events across:
1. SDN OpenFlow / Port Anomaly Alerts (VERIFIED_INTEGRATION)
2. Suricata IDS / Webhook Alerts (VERIFIED_INTEGRATION)
3. Perimeter Firewall Syslog / CEF Events (FIXTURE_SIMULATION)
4. Windows Server Security Event Logs - Event IDs 4625/5157 (FIXTURE_SIMULATION)

Explicitly marks simulated sources as FIXTURE_SIMULATION so academic and
engineering reports never conflate fixture validation with live log shipping.
"""

from __future__ import annotations

import ipaddress
import re
from typing import Any

FIREWALL_SYSLOG_REGEX = re.compile(
    r"Action=(?P<action>ALLOW|DROP|REJECT)\s+"
    r"Proto=(?P<proto>TCP|UDP|ICMP)\s+"
    r"Src=(?P<src>(?:\d{1,3}\.){3}\d{1,3})\s+"
    r"Dst=(?P<dst>(?:\d{1,3}\.){3}\d{1,3})\s+"
    r"Spt=(?P<spt>\d+)\s+Dpt=(?P<dpt>\d+)",
    re.IGNORECASE,
)


def _safe_ip(value: Any) -> str | None:
    if not value:
        return None
    try:
        return str(ipaddress.ip_address(str(value).strip()))
    except Exception:
        return None


def normalize_firewall_log(raw_event: dict[str, Any] | str) -> dict[str, Any]:
    """Normalize a Firewall syslog string or structured dict into SDNFlowGuard SIEM schema."""
    if isinstance(raw_event, str):
        match = FIREWALL_SYSLOG_REGEX.search(raw_event)
        if not match:
            raise ValueError(f"Unsupported firewall log format: {raw_event[:120]}")
        parsed = match.groupdict()
        src_ip = _safe_ip(parsed["src"])
        dst_ip = _safe_ip(parsed["dst"])
        action = parsed["action"].upper()
        proto = parsed["proto"].upper()
        src_port = int(parsed["spt"])
        dst_port = int(parsed["dpt"])
        timestamp = None
        rule_id = "FW_PERIMETER_RULE"
    elif isinstance(raw_event, dict):
        src_ip = _safe_ip(raw_event.get("src_ip") or raw_event.get("source_ip"))
        dst_ip = _safe_ip(raw_event.get("dst_ip") or raw_event.get("destination_ip"))
        action = str(raw_event.get("action") or "DROP").upper()
        proto = str(raw_event.get("protocol") or "TCP").upper()
        src_port = int(raw_event.get("src_port", 0))
        dst_port = int(raw_event.get("dst_port", 0))
        timestamp = raw_event.get("@timestamp") or raw_event.get("timestamp")
        rule_id = str(raw_event.get("rule_id") or "FW_PERIMETER_RULE")
    else:
        raise ValueError("Firewall event must be a string or dict")

    if not src_ip or not dst_ip:
        raise ValueError("Firewall event missing valid source or destination IP")

    severity = "HIGH" if action in ("DROP", "REJECT") else "INFO"
    return {
        "schema_version": 1,
        "event_category": "siem_normalized_event",
        "source_system": "FIREWALL",
        "integration_status": "FIXTURE_SIMULATION",
        "@timestamp": timestamp or "2026-11-05T00:00:00Z",
        "rule_id": rule_id,
        "action": action,
        "severity": severity,
        "protocol": proto,
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "source_port": src_port,
        "destination_port": dst_port,
        "sdn_correlation_eligible": True,
        "automatic_block_allowed": False,
        "note": "Normalized from Firewall fixture; live Firewall syslog shipper is not connected in lab workspace.",
    }


def normalize_windows_event_log(raw_event: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Windows Server Security Event (e.g. 4625 Failed Logon, 5157 WFP Block)."""
    if not isinstance(raw_event, dict):
        raise ValueError("Windows Event Log record must be a dict")

    event_id = int(raw_event.get("EventID") or raw_event.get("event_id") or 0)
    if event_id not in (4624, 4625, 5156, 5157, 4688):
        raise ValueError(f"Unsupported Windows Security EventID: {event_id}")

    src_ip = _safe_ip(
        raw_event.get("IpAddress")
        or raw_event.get("SourceAddress")
        or raw_event.get("source_ip")
    )
    dst_ip = _safe_ip(
        raw_event.get("DestAddress")
        or raw_event.get("destination_ip")
        or "10.0.0.10"
    )
    account = str(raw_event.get("TargetUserName") or raw_event.get("account") or "SYSTEM")
    computer = str(raw_event.get("Computer") or raw_event.get("host") or "WIN-SRV01.lab.local")
    timestamp = raw_event.get("@timestamp") or raw_event.get("TimeCreated") or "2026-11-05T00:00:00Z"

    event_descriptions = {
        4624: ("ALLOW", "INFO", "Windows Account Successful Logon"),
        4625: ("OBSERVE", "HIGH", "Windows Account Failed Logon (Brute-Force Candidate)"),
        5156: ("ALLOW", "INFO", "Windows Filtering Platform Permitted Connection"),
        5157: ("DROP", "HIGH", "Windows Filtering Platform Blocked Connection"),
        4688: ("OBSERVE", "MEDIUM", "Windows New Process Created"),
    }
    action, severity, summary = event_descriptions[event_id]

    return {
        "schema_version": 1,
        "event_category": "siem_normalized_event",
        "source_system": "WINDOWS_SERVER",
        "integration_status": "FIXTURE_SIMULATION",
        "@timestamp": timestamp,
        "event_id": event_id,
        "computer": computer,
        "target_account": account,
        "action": action,
        "severity": severity,
        "summary": summary,
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "sdn_correlation_eligible": bool(src_ip),
        "automatic_block_allowed": False,
        "note": "Normalized from Windows Event Log fixture; live Winlogbeat agent is not connected in lab workspace.",
    }


def evaluate_siem_capabilities() -> dict[str, Any]:
    """Run built-in fixture verification for SIEM multi-source normalization."""
    fw_sample = (
        "2026-11-05T01:15:00Z fw01 kernel: Action=DROP Proto=TCP "
        "Src=10.0.0.1 Dst=10.0.0.2 Spt=51422 Dpt=22"
    )
    win_sample_4625 = {
        "@timestamp": "2026-11-05T01:16:00Z",
        "EventID": 4625,
        "Computer": "WIN-DC01.sdn.lab",
        "TargetUserName": "Administrator",
        "IpAddress": "10.0.0.1",
        "DestAddress": "10.0.0.2",
    }
    win_sample_5157 = {
        "@timestamp": "2026-11-05T01:16:05Z",
        "EventID": 5157,
        "Computer": "WIN-DC01.sdn.lab",
        "TargetUserName": "NETWORK SERVICE",
        "SourceAddress": "10.0.0.1",
        "DestAddress": "10.0.0.2",
    }

    normalized_fw = normalize_firewall_log(fw_sample)
    normalized_win_4625 = normalize_windows_event_log(win_sample_4625)
    normalized_win_5157 = normalize_windows_event_log(win_sample_5157)

    return {
        "sources": [
            {
                "source_system": "ONOS_OPENFLOW_COLLECTOR",
                "integration_status": "VERIFIED_INTEGRATION",
                "transport": "REST / Elasticsearch / Logstash TCP 18080",
                "description": "Collects switch flows, port counters, and LAB_HIGH_PPS_AUTO_V1 anomaly alerts.",
            },
            {
                "source_system": "SURICATA_WEBHOOK_RECEPTION",
                "integration_status": "VERIFIED_INTEGRATION",
                "transport": "HTTP POST /webhook -> SQLite & Risk Scoring Engine",
                "description": "Receives IDS alerts and updates IP trust scores.",
            },
            {
                "source_system": "FIREWALL_SYSLOG",
                "integration_status": "FIXTURE_SIMULATION",
                "transport": "Normalized via sdnflowguard.domain.services.siem_log_normalizer",
                "description": "Parses perimeter Firewall ALLOW/DROP/REJECT events for SDN cross-correlation.",
                "sample_normalized": normalized_fw,
            },
            {
                "source_system": "WINDOWS_SERVER_EVENTLOG",
                "integration_status": "FIXTURE_SIMULATION",
                "transport": "Normalized via sdnflowguard.domain.services.siem_log_normalizer",
                "description": "Parses Windows Security Event IDs 4624/4625/5156/5157 for host-level correlation.",
                "sample_normalized": [normalized_win_4625, normalized_win_5157],
            },
        ],
        "verified_count": 2,
        "fixture_simulation_count": 2,
    }

