"""Application use cases orchestrating domain policies and infrastructure ports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from defense.onos_host_evidence_correlator import (
    DEFAULT_EVIDENCE_PATH,
    DEFAULT_LAB_TOPOLOGY,
    correlate_step63_evidence_file,
)
from sdnflowguard.domain.policies.defense_policy import evaluate_defense_policy
from sdnflowguard.domain.policies.safety_gate import evaluate_safety_gate
from sdnflowguard.domain.services.siem_log_normalizer import evaluate_siem_capabilities
from sdnflowguard.infrastructure.configuration.settings import AppSettings
from sdnflowguard.observability.structured_logger import generate_request_id


def run_step64_evidence_correlation_use_case(
    *,
    evidence_path: Path | None = None,
    topology: dict[str, Any] | None = None,
    capture_metadata: dict[str, Any] | None = None,
    alerts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute Step 64 ONOS host evidence correlation and return structured report."""
    target = evidence_path or DEFAULT_EVIDENCE_PATH
    report = correlate_step63_evidence_file(
        target,
        topology=topology,
        capture_metadata=capture_metadata,
        alerts=alerts,
    )
    report["request_id"] = generate_request_id()
    return report


def run_defense_policy_evaluation_use_case(
    *,
    device_id: str = "of:0000000000000001",
    topology: dict[str, Any] | None = None,
    alerts: list[dict[str, Any]] | None = None,
    include_step64_evidence: bool = True,
) -> dict[str, Any]:
    """Evaluate defense policy across switch ports with Step 64 evidence integration."""
    topo = topology if isinstance(topology, dict) else DEFAULT_LAB_TOPOLOGY
    sample_alerts = (
        alerts
        if isinstance(alerts, list)
        else [
            {
                "switch_id": device_id,
                "port_number": "1",
                "test_only": True,
                "peak_pps": 10.152,
                "rule_id": "LAB_HIGH_PPS_AUTO_V1",
            }
        ]
    )

    evidence_data = None
    if include_step64_evidence and DEFAULT_EVIDENCE_PATH.is_file():
        import json

        with DEFAULT_EVIDENCE_PATH.open("r", encoding="utf-8-sig") as fh:
            evidence_data = json.load(fh)

    reports = evaluate_defense_policy(
        device_id,
        topo.get("ports") or [],
        topo.get("hosts") or [],
        topo.get("flows") or [],
        sample_alerts,
        evidence=evidence_data,
    )

    settings = AppSettings.from_env()
    return {
        "request_id": generate_request_id(),
        "device_id": device_id,
        "defense_mode": settings.defense_mode,
        "topology_source": "LIVE_ONOS" if topology is not None else "REFERENCE_LAB_TOPOLOGY_FIXTURE",
        "port_decisions": reports,
        "summary": {
            "ALLOW": sum(1 for r in reports if r["decision"] == "ALLOW"),
            "OBSERVE": sum(1 for r in reports if r["decision"] == "OBSERVE"),
            "PROPOSE_BLOCK": sum(1 for r in reports if r["decision"] == "PROPOSE_BLOCK"),
        },
    }


def evaluate_control_action_safety_use_case(
    *,
    action_type: str,
    target_ip: str | None = None,
    target_device_id: str | None = "of:0000000000000001",
    target_port: str | None = None,
    explicit_dry_run: bool | None = None,
    operator_approved: bool = False,
    manual_operator_override: bool = True,
    test_only: bool = False,
    source_ip_attributed: bool = False,
    historical_alert_correlation_verified: bool = False,
    controller_ip: str | None = None,
    elk_ip: str | None = None,
) -> dict[str, Any]:
    """Evaluate a proposed control action against the Active Defense Safety Gate."""
    settings = AppSettings.from_env()
    verdict = evaluate_safety_gate(
        action_type=action_type,
        defense_mode=settings.defense_mode,
        target_ip=target_ip,
        target_device_id=target_device_id,
        target_port=target_port,
        test_only=test_only,
        source_ip_attributed=source_ip_attributed,
        historical_alert_correlation_verified=historical_alert_correlation_verified,
        manual_operator_override=manual_operator_override,
        operator_approved=operator_approved,
        allowlist_ips=settings.allowlist_ips,
        controller_ip=controller_ip,
        elk_ip=elk_ip,
        explicit_dry_run=explicit_dry_run,
    )
    return verdict.to_dict()


def run_siem_capability_evaluation_use_case() -> dict[str, Any]:
    """Run SIEM multi-source normalization evaluation (SDN + Suricata + Firewall + Windows)."""
    result = evaluate_siem_capabilities()
    result["request_id"] = generate_request_id()
    return result

