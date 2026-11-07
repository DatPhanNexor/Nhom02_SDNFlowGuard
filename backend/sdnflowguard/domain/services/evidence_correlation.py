"""Step 64: ONOS Host Evidence Correlation domain service.

Correlates switch ingress packet observations (Step 63) with ONOS topology
state (devices, ports, hosts, flows) and optional Elasticsearch alert windows.
Enforces strict timestamp & provenance verification rules.
"""

from __future__ import annotations

import hashlib
import ipaddress
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sdnflowguard.domain.exceptions import EvidenceCorrelationError
from sdnflowguard.domain.models import (
    CaptureMetadata,
    CorrelationStatus,
    HostCorrelationResult,
    PolicyDecisionType,
)

MAC_PATTERN = re.compile(r"^(?:[0-9a-f]{2}:){5}[0-9a-f]{2}$", re.IGNORECASE)
CLOCK_PATTERN = re.compile(r"^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(?:\.(?P<micro>\d+))?$")


def validate_mac(mac: Any) -> str:
    """Validate and normalize a MAC address string."""
    if not isinstance(mac, str) or not MAC_PATTERN.match(mac.strip()):
        raise ValueError(f"Invalid MAC address: {mac!r}")
    return mac.strip().lower()


def validate_ip(ip_str: Any) -> str:
    """Validate and normalize an IPv4 or IPv6 address string."""
    if not isinstance(ip_str, str) or not ip_str.strip():
        raise ValueError(f"Invalid IP address: {ip_str!r}")
    return str(ipaddress.ip_address(ip_str.strip()))


def parse_iso8601_utc(ts_str: Any) -> datetime:
    """Parse an ISO-8601 timestamp string and require explicit timezone awareness."""
    if not isinstance(ts_str, str) or not ts_str.strip():
        raise ValueError("Empty timestamp string")
    raw = ts_str.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        raise ValueError(f"Timestamp lacks explicit timezone offset: {ts_str!r}")
    return dt.astimezone(timezone.utc)


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def index_hosts_by_port(hosts: list[dict[str, Any]], device_id: str) -> dict[str, list[dict[str, Any]]]:
    """Group ONOS hosts by port number on a given switch device_id."""
    mapping: dict[str, list[dict[str, Any]]] = {}
    for host in hosts or []:
        if not isinstance(host, dict):
            continue
        raw_ips = host.get("ipAddresses") or []
        ips = [str(ip).strip() for ip in raw_ips if str(ip).strip()]
        mac = str(host.get("mac") or "").strip().lower()
        locations = host.get("locations") or []
        for location in locations:
            if not isinstance(location, dict):
                continue
            if location.get("elementId") != device_id:
                continue
            port = str(location.get("port") or "").strip()
            if not port:
                continue
            mapping.setdefault(port, []).append(
                {
                    "id": host.get("id") or f"{mac}/None",
                    "mac": mac,
                    "ips": ips,
                    "vlan": host.get("vlan", "None"),
                }
            )
    return mapping


def count_ip_source_flows(flows: list[dict[str, Any]]) -> int:
    """Count ONOS flow rules that match on IPV4_SRC or IPV6_SRC criteria."""
    count = 0
    for flow in flows or []:
        if not isinstance(flow, dict):
            continue
        selector = flow.get("selector") or {}
        criteria = selector.get("criteria") or []
        if any(
            isinstance(item, dict) and item.get("type") in ("IPV4_SRC", "IPV6_SRC")
            for item in criteria
        ):
            count += 1
    return count


def verify_capture_time_window(
    evidence: dict[str, Any],
    capture_metadata: CaptureMetadata | dict[str, Any] | None = None,
    alerts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Verify whether packet capture timestamps can be correlated with historical alerts."""
    has_date = bool(evidence.get("capture_clock_has_date", False))
    has_tz = bool(evidence.get("capture_clock_has_timezone", False))

    meta_dict: dict[str, Any] = {}
    if isinstance(capture_metadata, CaptureMetadata):
        meta_dict = capture_metadata.to_dict()
    elif isinstance(capture_metadata, dict):
        meta_dict = dict(capture_metadata)
    elif isinstance(evidence.get("capture_metadata"), dict):
        meta_dict = dict(evidence["capture_metadata"])

    started_utc_str = meta_dict.get("capture_started_utc")
    finished_utc_str = meta_dict.get("capture_finished_utc")

    started_dt: datetime | None = None
    finished_dt: datetime | None = None
    metadata_valid = False
    metadata_error: str | None = None

    if started_utc_str and finished_utc_str:
        try:
            started_dt = parse_iso8601_utc(started_utc_str)
            finished_dt = parse_iso8601_utc(finished_utc_str)
            if finished_dt < started_dt:
                metadata_error = "capture_finished_utc is earlier than capture_started_utc"
            else:
                metadata_valid = True
        except Exception as exc:
            metadata_error = f"Invalid capture UTC metadata: {exc}"

    effective_has_full_time = (has_date and has_tz) or metadata_valid

    if not effective_has_full_time:
        reason = (
            metadata_error
            if metadata_error
            else (
                "Packet capture clock only records time-of-day (HH:MM:SS.us) without date "
                "or timezone (capture_clock_has_date=False, capture_clock_has_timezone=False). "
                "Historical alert correlation cannot be verified without full UTC window metadata."
            )
        )
        return {
            "capture_clock_has_date": has_date,
            "capture_clock_has_timezone": has_tz,
            "metadata_window_valid": False,
            "capture_started_utc": started_utc_str,
            "capture_finished_utc": finished_utc_str,
            "matching_alerts_in_window": 0,
            "non_test_alerts_in_window": 0,
            "historical_alert_correlation_verified": False,
            "reason": reason,
        }

    # If full UTC window is available, check alerts falling inside the window
    matching_alerts = []
    non_test_alerts = []
    if started_dt and finished_dt and alerts:
        for alert in alerts:
            if not isinstance(alert, dict):
                continue
            ts = alert.get("@timestamp")
            if not ts:
                continue
            try:
                alert_dt = parse_iso8601_utc(ts)
            except Exception:
                continue
            if started_dt <= alert_dt <= finished_dt:
                matching_alerts.append(alert)
                if alert.get("test_only") is not True:
                    non_test_alerts.append(alert)

    verified = bool(non_test_alerts)
    if verified:
        reason = (
            f"Verified {len(non_test_alerts)} non-test alert(s) within explicit UTC capture window "
            f"[{started_dt.isoformat()} .. {finished_dt.isoformat()}]."
        )
    elif matching_alerts:
        reason = (
            f"Found {len(matching_alerts)} alert(s) in UTC capture window, but all are marked "
            "test_only=True; test alerts cannot authorize active blocking."
        )
    else:
        reason = "Full UTC capture window verified, but no matching alerts occurred during the capture window."

    return {
        "capture_clock_has_date": has_date or metadata_valid,
        "capture_clock_has_timezone": has_tz or metadata_valid,
        "metadata_window_valid": metadata_valid,
        "capture_started_utc": started_dt.isoformat() if started_dt else started_utc_str,
        "capture_finished_utc": finished_dt.isoformat() if finished_dt else finished_utc_str,
        "matching_alerts_in_window": len(matching_alerts),
        "non_test_alerts_in_window": len(non_test_alerts),
        "historical_alert_correlation_verified": verified,
        "reason": reason,
    }


def correlate_single_observation(
    obs: dict[str, Any],
    *,
    devices: list[dict[str, Any]] | None,
    ports_by_device: dict[str, dict[str, dict[str, Any]]],
    hosts_by_device_port: dict[str, dict[str, list[dict[str, Any]]]],
    ip_source_flow_count: int,
    time_verification: dict[str, Any],
) -> HostCorrelationResult:
    """Correlate a single packet observation record against ONOS topology state."""
    raw_switch = str(obs.get("switch_id") or "").strip()
    raw_port = str(obs.get("ingress_port") or "").strip()
    raw_iface = str(obs.get("interface") or "").strip()
    raw_mac = obs.get("observed_source_mac")
    raw_src_ip = obs.get("observed_source_ip")
    raw_dst_ip = obs.get("observed_destination_ip") or "0.0.0.0"
    protocol = str(obs.get("protocol") or "UNKNOWN").upper()
    icmp_type = str(obs.get("icmp_type") or "none").lower()
    packet_count = obs.get("packet_count", 0)

    # 1. Validate observation data integrity
    try:
        if not raw_switch or not raw_port or raw_port == "local":
            raise ValueError("Missing or invalid switch_id / ingress_port")
        norm_mac = validate_mac(raw_mac)
        norm_src_ip = validate_ip(raw_src_ip)
        norm_dst_ip = validate_ip(raw_dst_ip)
        if not isinstance(packet_count, int) or isinstance(packet_count, bool) or packet_count <= 0:
            raise ValueError(f"Invalid packet_count: {packet_count!r}")
    except Exception as exc:
        return HostCorrelationResult(
            switch_id=raw_switch or "UNKNOWN",
            ingress_port=raw_port or "UNKNOWN",
            interface=raw_iface or "UNKNOWN",
            observed_source_mac=str(raw_mac or ""),
            observed_source_ip=str(raw_src_ip or ""),
            observed_destination_ip=str(raw_dst_ip or ""),
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count if isinstance(packet_count, int) else 0,
            device_present=False,
            port_present=False,
            port_enabled=False,
            attached_host_count=0,
            attached_hosts=[],
            mac_matched=False,
            ip_matched=False,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.INVALID_EVIDENCE_DATA.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=f"Invalid observation data: {exc}",
        )

    # 2. Check switch device availability
    device_present = True
    if devices is not None:
        matched_devices = [
            d for d in devices if isinstance(d, dict) and d.get("id") == raw_switch
        ]
        if not matched_devices or not matched_devices[0].get("available", True):
            device_present = False

    if not device_present:
        return HostCorrelationResult(
            switch_id=raw_switch,
            ingress_port=raw_port,
            interface=raw_iface,
            observed_source_mac=norm_mac,
            observed_source_ip=norm_src_ip,
            observed_destination_ip=norm_dst_ip,
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count,
            device_present=False,
            port_present=False,
            port_enabled=False,
            attached_host_count=0,
            attached_hosts=[],
            mac_matched=False,
            ip_matched=False,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.DEVICE_UNAVAILABLE.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=f"Switch {raw_switch} is missing or unavailable in ONOS topology.",
        )

    # 3. Check port presence and enabled state
    device_ports = ports_by_device.get(raw_switch, {})
    port_info = device_ports.get(raw_port)
    port_present = port_info is not None
    port_enabled = bool(port_info.get("isEnabled", False)) if port_info else False

    attached_hosts = hosts_by_device_port.get(raw_switch, {}).get(raw_port, [])
    attached_count = len(attached_hosts)

    if not port_present or not port_enabled:
        return HostCorrelationResult(
            switch_id=raw_switch,
            ingress_port=raw_port,
            interface=raw_iface,
            observed_source_mac=norm_mac,
            observed_source_ip=norm_src_ip,
            observed_destination_ip=norm_dst_ip,
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count,
            device_present=True,
            port_present=port_present,
            port_enabled=port_enabled,
            attached_host_count=attached_count,
            attached_hosts=attached_hosts,
            mac_matched=False,
            ip_matched=False,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.PORT_UNAVAILABLE_OR_DISABLED.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=(
                f"Port {raw_port} on {raw_switch} is "
                f"{'missing' if not port_present else 'disabled (isEnabled=False)'} in ONOS."
            ),
        )

    # 4. Correlate against ONOS attached hosts on (switch_id, ingress_port)
    if attached_count == 0:
        return HostCorrelationResult(
            switch_id=raw_switch,
            ingress_port=raw_port,
            interface=raw_iface,
            observed_source_mac=norm_mac,
            observed_source_ip=norm_src_ip,
            observed_destination_ip=norm_dst_ip,
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count,
            device_present=True,
            port_present=True,
            port_enabled=True,
            attached_host_count=0,
            attached_hosts=[],
            mac_matched=False,
            ip_matched=False,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.UNREGISTERED_HOST_ON_PORT.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=(
                f"Packet observed on {raw_switch}/{raw_port} from {norm_src_ip} ({norm_mac}), "
                "but ONOS reports 0 attached hosts on this port."
            ),
        )

    if attached_count > 1:
        mac_matched = any(h.get("mac") == norm_mac for h in attached_hosts)
        ip_matched = any(
            h.get("mac") == norm_mac and norm_src_ip in (h.get("ips") or [])
            for h in attached_hosts
        )
        return HostCorrelationResult(
            switch_id=raw_switch,
            ingress_port=raw_port,
            interface=raw_iface,
            observed_source_mac=norm_mac,
            observed_source_ip=norm_src_ip,
            observed_destination_ip=norm_dst_ip,
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count,
            device_present=True,
            port_present=True,
            port_enabled=True,
            attached_host_count=attached_count,
            attached_hosts=attached_hosts,
            mac_matched=mac_matched,
            ip_matched=ip_matched,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.AMBIGUOUS_MULTI_HOST.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=(
                f"Port {raw_switch}/{raw_port} has {attached_count} hosts attached in ONOS; "
                "multi-host port requires per-flow/MAC isolation before any port or host enforcement."
            ),
        )

    # Exactly 1 host attached on this port
    single_host = attached_hosts[0]
    host_mac = str(single_host.get("mac") or "").lower()
    host_ips = [str(ip) for ip in (single_host.get("ips") or [])]

    mac_matched = host_mac == norm_mac
    ip_matched = norm_src_ip in host_ips

    if not (mac_matched and ip_matched):
        mismatch_details = []
        if not mac_matched:
            mismatch_details.append(f"observed MAC {norm_mac} != ONOS host MAC {host_mac}")
        if not ip_matched:
            mismatch_details.append(f"observed IP {norm_src_ip} not in ONOS host IPs {host_ips}")
        return HostCorrelationResult(
            switch_id=raw_switch,
            ingress_port=raw_port,
            interface=raw_iface,
            observed_source_mac=norm_mac,
            observed_source_ip=norm_src_ip,
            observed_destination_ip=norm_dst_ip,
            protocol=protocol,
            icmp_type=icmp_type,
            packet_count=packet_count,
            device_present=True,
            port_present=True,
            port_enabled=True,
            attached_host_count=1,
            attached_hosts=attached_hosts,
            mac_matched=mac_matched,
            ip_matched=ip_matched,
            ip_source_flow_count=ip_source_flow_count,
            correlation_status=CorrelationStatus.HOST_IDENTITY_MISMATCH.value,
            topology_corroborated=False,
            attacker_confirmed=False,
            historical_alert_correlation_verified=False,
            recommended_decision=PolicyDecisionType.OBSERVE.value,
            automatic_block_allowed=False,
            rationale=(
                f"Host identity mismatch on {raw_switch}/{raw_port} "
                f"({'; '.join(mismatch_details)}). Possible IP/MAC spoofing or stale ONOS host table."
            ),
        )

    # Topology matches 1-to-1: (switch_id, ingress_port, MAC, IP) corroborated!
    hist_verified = bool(time_verification.get("historical_alert_correlation_verified", False))
    is_benign_icmp_sample = protocol == "ICMP" and icmp_type in ("request", "reply") and packet_count < 1000

    if not hist_verified:
        rationale = (
            f"ONOS topology corroborates host {norm_src_ip} ({norm_mac}) on {raw_switch} port {raw_port}, "
            f"but historical alert correlation is unverified ({time_verification.get('reason')}). "
            "Decision remains OBSERVE."
        )
    elif is_benign_icmp_sample:
        rationale = (
            f"ONOS topology and UTC window verified for {norm_src_ip} ({norm_mac}) on {raw_switch} port {raw_port}, "
            f"but observed packets ({packet_count} ICMP {icmp_type}) represent normal diagnostic ping traffic, "
            "not a confirmed flood attack. Decision remains OBSERVE."
        )
    else:
        rationale = (
            f"ONOS topology, UTC window, and high-volume packet evidence corroborated for {norm_src_ip} "
            f"({norm_mac}) on {raw_switch} port {raw_port}. Eligible for PROPOSE_BLOCK subject to Safety Gate."
        )

    attacker_confirmed = bool(hist_verified and not is_benign_icmp_sample)
    recommended_decision = (
        PolicyDecisionType.PROPOSE_BLOCK.value
        if attacker_confirmed
        else PolicyDecisionType.OBSERVE.value
    )

    return HostCorrelationResult(
        switch_id=raw_switch,
        ingress_port=raw_port,
        interface=raw_iface,
        observed_source_mac=norm_mac,
        observed_source_ip=norm_src_ip,
        observed_destination_ip=norm_dst_ip,
        protocol=protocol,
        icmp_type=icmp_type,
        packet_count=packet_count,
        device_present=True,
        port_present=True,
        port_enabled=True,
        attached_host_count=1,
        attached_hosts=attached_hosts,
        mac_matched=True,
        ip_matched=True,
        ip_source_flow_count=ip_source_flow_count,
        correlation_status=CorrelationStatus.CORROBORATED_HOST_OBSERVATION.value,
        topology_corroborated=True,
        attacker_confirmed=attacker_confirmed,
        historical_alert_correlation_verified=hist_verified,
        recommended_decision=recommended_decision,
        automatic_block_allowed=False,
        rationale=rationale,
    )


def correlate_evidence_with_onos(
    evidence: dict[str, Any],
    *,
    device_id: str = "of:0000000000000001",
    ports: list[dict[str, Any]] | None = None,
    hosts: list[dict[str, Any]] | None = None,
    flows: list[dict[str, Any]] | None = None,
    devices: list[dict[str, Any]] | None = None,
    alerts: list[dict[str, Any]] | None = None,
    capture_metadata: CaptureMetadata | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Correlate a full Step 63 packet evidence payload against ONOS state (Step 64)."""
    if not isinstance(evidence, dict):
        raise EvidenceCorrelationError("Evidence payload must be a JSON object (dict)")

    observations = evidence.get("observations")
    if not isinstance(observations, list) or not observations:
        raise EvidenceCorrelationError("Evidence payload must contain a non-empty 'observations' list")

    ports_list = ports if isinstance(ports, list) else []
    hosts_list = hosts if isinstance(hosts, list) else []
    flows_list = flows if isinstance(flows, list) else []

    ports_by_device: dict[str, dict[str, dict[str, Any]]] = {device_id: {}}
    for port_entry in ports_list:
        if not isinstance(port_entry, dict):
            continue
        p_num = str(port_entry.get("port") or "").strip()
        p_dev = str(port_entry.get("element") or device_id).strip()
        if p_num:
            ports_by_device.setdefault(p_dev, {})[p_num] = port_entry

    # Index hosts across all referenced devices
    referenced_devices = {device_id}
    for obs in observations:
        if isinstance(obs, dict) and obs.get("switch_id"):
            referenced_devices.add(str(obs["switch_id"]).strip())

    hosts_by_device_port: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for dev in referenced_devices:
        hosts_by_device_port[dev] = index_hosts_by_port(hosts_list, dev)

    ip_source_flow_count = count_ip_source_flows(flows_list)
    time_verification = verify_capture_time_window(
        evidence,
        capture_metadata=capture_metadata,
        alerts=alerts,
    )

    correlation_results: list[dict[str, Any]] = []
    for obs in observations:
        if not isinstance(obs, dict):
            obs = {}
        result = correlate_single_observation(
            obs,
            devices=devices,
            ports_by_device=ports_by_device,
            hosts_by_device_port=hosts_by_device_port,
            ip_source_flow_count=ip_source_flow_count,
            time_verification=time_verification,
        )
        correlation_results.append(result.to_dict())

    all_corroborated = all(r["topology_corroborated"] for r in correlation_results)
    any_attacker_confirmed = any(r["attacker_confirmed"] for r in correlation_results)
    overall_decision = (
        PolicyDecisionType.PROPOSE_BLOCK.value
        if any_attacker_confirmed
        else PolicyDecisionType.OBSERVE.value
    )

    return {
        "schema_version": 2,
        "step": "STEP_64_ONOS_HOST_EVIDENCE_CORRELATION",
        "evidence_type": "onos_host_correlated_packet_observation",
        "device_id": device_id,
        "total_packets": evidence.get("total_packets", 0),
        "first_packet_clock": evidence.get("first_packet_clock"),
        "last_packet_clock": evidence.get("last_packet_clock"),
        "time_verification": time_verification,
        "topology_snapshot_summary": {
            "onos_device_count": len(devices) if isinstance(devices, list) else 1,
            "onos_port_count": len([p for p in ports_list if isinstance(p, dict) and str(p.get("port")) != "local"]),
            "onos_host_count": len(hosts_list),
            "onos_flow_count": len(flows_list),
            "ip_source_selector_flows": ip_source_flow_count,
        },
        "correlated_observations": correlation_results,
        "security_assessment": {
            "source_ip_observed": True,
            "topology_corroborated": all_corroborated,
            "attacker_confirmed": any_attacker_confirmed,
            "historical_alert_correlation_verified": time_verification["historical_alert_correlation_verified"],
            "decision": overall_decision,
            "automatic_block_allowed": False,
        },
    }

