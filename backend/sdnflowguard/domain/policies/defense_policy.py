"""Defense policy evaluation engine combining port alerts and Step 64 evidence."""

from __future__ import annotations

from typing import Any

from sdnflowguard.domain.models import PolicyDecisionType
from sdnflowguard.domain.services.evidence_correlation import (
    correlate_evidence_with_onos,
    count_ip_source_flows,
    index_hosts_by_port,
)

DECISIONS = (
    PolicyDecisionType.ALLOW.value,
    PolicyDecisionType.OBSERVE.value,
    PolicyDecisionType.PROPOSE_BLOCK.value,
)


def evaluate_defense_policy(
    device_id: str,
    ports: list[dict[str, Any]],
    hosts: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    alerts: list[dict[str, Any]],
    *,
    evidence: dict[str, Any] | None = None,
    capture_metadata: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate per-port defense policy with optional Step 64 evidence correlation.

    Maintains 100% backward compatibility with the 5-argument signature in
    `backend/defense/sdn_defense_policy.py` while enriching reports when Step 64
    evidence is provided.
    """
    host_mapping = index_hosts_by_port(hosts, device_id)
    source_flows = count_ip_source_flows(flows)

    correlated_by_port: dict[str, list[dict[str, Any]]] = {}
    if isinstance(evidence, dict) and evidence.get("observations"):
        corr_report = correlate_evidence_with_onos(
            evidence,
            device_id=device_id,
            ports=ports,
            hosts=hosts,
            flows=flows,
            alerts=alerts,
            capture_metadata=capture_metadata,
        )
        for item in corr_report.get("correlated_observations", []):
            if item.get("switch_id") == device_id:
                p_str = str(item.get("ingress_port") or "")
                correlated_by_port.setdefault(p_str, []).append(item)

    reports: list[dict[str, Any]] = []

    for port_info in ports or []:
        if not isinstance(port_info, dict):
            continue
        port = str(port_info.get("port"))
        if port == "local":
            continue

        related = [
            alert
            for alert in (alerts or [])
            if isinstance(alert, dict)
            and alert.get("switch_id") == device_id
            and str(alert.get("port_number")) == port
        ]

        connected_hosts = [
            {"mac": h["mac"], "ips": h["ips"]}
            for h in host_mapping.get(port, [])
        ]
        port_correlations = correlated_by_port.get(port, [])
        all_test_alerts = bool(related) and all(
            alert.get("test_only") is True for alert in related
        )
        any_attacker_confirmed = any(
            c.get("attacker_confirmed") is True for c in port_correlations
        )

        if not related:
            decision = PolicyDecisionType.ALLOW.value
            reason = "No matching alert in selected time range."
            source_ip_attributed = False
        elif all_test_alerts:
            decision = PolicyDecisionType.OBSERVE.value
            reason = "Port-level anomaly only; source IP not independently verified."
            source_ip_attributed = False
        elif any_attacker_confirmed:
            decision = PolicyDecisionType.PROPOSE_BLOCK.value
            reason = (
                "Non-test port anomaly corroborated by Step 64 ONOS host topology, "
                "packet source IP/MAC, and verified UTC capture window."
            )
            source_ip_attributed = True
        else:
            decision = PolicyDecisionType.OBSERVE.value
            reason = "Port-level anomaly only; source IP not independently verified."
            source_ip_attributed = False

        report_entry: dict[str, Any] = {
            "switch_id": device_id,
            "port_number": port,
            "port_enabled": bool(port_info.get("isEnabled", False)),
            "attached_hosts": connected_hosts,
            "alert_count": len(related),
            "test_alert_count": sum(
                alert.get("test_only") is True for alert in related
            ),
            "source_ip_attributed": source_ip_attributed,
            "ip_source_flows_on_device": source_flows,
            "decision": decision,
            "reason": reason,
        }
        if evidence is not None:
            report_entry["step64_correlations"] = port_correlations
        reports.append(report_entry)

    return reports

