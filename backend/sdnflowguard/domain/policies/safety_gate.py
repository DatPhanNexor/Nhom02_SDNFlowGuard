"""Active Defense Safety Gate and Lifecycle State Machine.

Enforces fail-safe rules before any ONOS OpenFlow control action is proposed,
staged, or executed.

Lifecycle State Machine:
NORMAL -> ANOMALY_OBSERVED -> EVIDENCE_CORRELATED -> BLOCK_PROPOSED
       -> BLOCK_APPROVED -> RULE_APPLIED -> RULE_VERIFIED -> ROLLBACK_OR_EXPIRED
"""

from __future__ import annotations

import ipaddress
from typing import Any

from sdnflowguard.domain.models import (
    DefenseLifecycleState,
    DefenseMode,
    SafetyGateVerdict,
)

DEFAULT_PROTECTED_IPS = frozenset(
    {
        "127.0.0.1",
        "::1",
        "0.0.0.0",
        "255.255.255.255",
        "10.0.0.254",  # Default SDN Gateway / Infrastructure Router
        "8.8.8.8",     # Google Public DNS
        "1.1.1.1",     # Cloudflare Public DNS
    }
)


def is_protected_ip(
    ip_str: str | None,
    *,
    extra_allowlist: set[str] | list[str] | None = None,
    controller_ip: str | None = None,
    elk_ip: str | None = None,
) -> tuple[bool, str | None]:
    """Return (True, reason) if ip_str is invalid, loopback, multicast, broadcast, or overlaps protected infrastructure."""
    if not ip_str or not isinstance(ip_str, str):
        return True, "Missing or non-string target IP"

    cleaned = ip_str.strip()
    try:
        cand_net = ipaddress.ip_network(cleaned, strict=False)
    except (ValueError, TypeError):
        return True, f"Invalid IP/CIDR address syntax: {cleaned!r}"

    if cand_net.is_loopback:
        return True, f"IP/subnet {cleaned} is a loopback address space"
    if cand_net.is_multicast:
        return True, f"IP/subnet {cleaned} is a multicast address space"
    if cand_net.is_unspecified or cand_net.prefixlen == 0:
        return True, f"IP/subnet {cleaned} is an unspecified (0.0.0.0/::) or default route space"
    if cleaned in ("255.255.255.255", "255.255.255.255/32"):
        return True, "IP 255.255.255.255 is broadcast"

    allowset = set(DEFAULT_PROTECTED_IPS)
    if extra_allowlist:
        allowset.update(str(x).strip() for x in extra_allowlist if str(x).strip())
    if controller_ip:
        allowset.add(str(controller_ip).strip())
    if elk_ip:
        allowset.add(str(elk_ip).strip())

    for item in allowset:
        try:
            prot_net = ipaddress.ip_network(str(item).strip(), strict=False)
            if cand_net.overlaps(prot_net):
                return True, f"Target IP/subnet {cleaned} overlaps with protected infrastructure allowlist: {item}"
        except (ValueError, TypeError):
            continue

    return False, None


def evaluate_safety_gate(
    *,
    action_type: str,
    defense_mode: str = DefenseMode.DRY_RUN.value,
    target_ip: str | None = None,
    dst_ip: str | None = None,
    target_device_id: str | None = "of:0000000000000001",
    target_port: str | None = None,
    test_only: bool = False,
    source_ip_attributed: bool = False,
    historical_alert_correlation_verified: bool = False,
    manual_operator_override: bool = False,
    operator_approved: bool = False,
    operator_authenticated: bool = True,
    allowlist_ips: list[str] | set[str] | None = None,
    controller_ip: str | None = None,
    elk_ip: str | None = None,
    explicit_dry_run: bool | None = None,
) -> SafetyGateVerdict:
    """Evaluate all safety checks before proposing or executing an SDN control action."""
    mode_upper = str(defense_mode or DefenseMode.DRY_RUN.value).strip().upper()
    if mode_upper not in {m.value for m in DefenseMode}:
        mode_upper = DefenseMode.DRY_RUN.value

    # If backend policy is DRY_RUN or AUTO_STAGE_ONLY, client cannot force live execution
    if mode_upper in (DefenseMode.DRY_RUN.value, DefenseMode.AUTO_STAGE_ONLY.value):
        is_dry_run = True
    elif explicit_dry_run is not None:
        is_dry_run = bool(explicit_dry_run)
    else:
        is_dry_run = False

    rejection_reasons: list[str] = []
    safety_checks: dict[str, bool] = {
        "not_test_only_alert": not test_only,
        "valid_and_unprotected_target": True,
        "evidence_attribution_satisfied": False,
        "defense_mode_permits_execution": False,
        "operator_approval_satisfied": False,
    }

    if test_only:
        rejection_reasons.append(
            "Action rejected: source event is marked test_only=True (lab test alerts can never authorize enforcement)."
        )

    # Validate target IP and optional dst IP if action targets IP traffic
    ip_actions = {"block_ip", "unblock_ip", "throttle_traffic", "redirect_traffic", "prioritize_traffic"}
    port_actions = {"disable_port", "enable_port"}

    if action_type in ip_actions or target_ip is not None or dst_ip is not None:
        if target_ip is not None:
            protected, prot_reason = is_protected_ip(
                target_ip,
                extra_allowlist=allowlist_ips,
                controller_ip=controller_ip,
                elk_ip=elk_ip,
            )
            if protected:
                safety_checks["valid_and_unprotected_target"] = False
                rejection_reasons.append(f"Target IP check failed: {prot_reason}")

        if dst_ip is not None and dst_ip != target_ip:
            dst_protected, dst_prot_reason = is_protected_ip(
                dst_ip,
                extra_allowlist=allowlist_ips,
                controller_ip=controller_ip,
                elk_ip=elk_ip,
            )
            if dst_protected:
                safety_checks["valid_and_unprotected_target"] = False
                rejection_reasons.append(f"Destination IP check failed: {dst_prot_reason}")

    if action_type in port_actions:
        if not target_device_id or not target_port or str(target_port).strip().lower() == "local":
            safety_checks["valid_and_unprotected_target"] = False
            rejection_reasons.append(
                f"Target port check failed: invalid switch_id ({target_device_id!r}) or reserved port ({target_port!r})."
            )

    # Operator authentication verification
    is_operator_authenticated = bool(operator_authenticated)
    valid_operator_approval = (operator_approved or manual_operator_override) and is_operator_authenticated

    # Evidence attribution check: required for automated actions; authenticated manual operator override allowed in lab UI
    if (manual_operator_override and is_operator_authenticated) or action_type in ("unblock_ip", "enable_port"):
        safety_checks["evidence_attribution_satisfied"] = True
    elif source_ip_attributed and historical_alert_correlation_verified and not test_only:
        safety_checks["evidence_attribution_satisfied"] = True
    else:
        if manual_operator_override and not is_operator_authenticated:
            rejection_reasons.append(
                "Manual override rejected: evidence attribution bypass requires authenticated operator credentials."
            )
        else:
            rejection_reasons.append(
                "Automated enforcement requires Step 64 corroborated source IP attribution and verified UTC alert correlation."
            )

    # Operator approval check
    requires_manual = mode_upper == DefenseMode.MANUAL_APPROVAL.value
    if mode_upper == DefenseMode.ACTIVE_ENFORCEMENT.value:
        safety_checks["operator_approval_satisfied"] = True
    elif mode_upper == DefenseMode.MANUAL_APPROVAL.value and valid_operator_approval:
        safety_checks["operator_approval_satisfied"] = True
    else:
        if requires_manual:
            if (operator_approved or manual_operator_override) and not is_operator_authenticated:
                rejection_reasons.append(
                    "Action rejected: manual operator approval requires authenticated operator credentials (unauthenticated client parameter elevation is prohibited)."
                )
            else:
                rejection_reasons.append(
                    "Defense mode is MANUAL_APPROVAL and operator_approved=False."
                )

    # Defense mode execution check
    if not is_dry_run and mode_upper in (
        DefenseMode.MANUAL_APPROVAL.value,
        DefenseMode.ACTIVE_ENFORCEMENT.value,
    ):
        safety_checks["defense_mode_permits_execution"] = True
    else:
        rejection_reasons.append(
            f"Defense mode is {mode_upper} (dry_run={is_dry_run}); action is simulated/staged without modifying ONOS."
        )

    allowed_to_execute = all(safety_checks.values()) and not is_dry_run

    # Determine lifecycle state
    if test_only or not safety_checks["valid_and_unprotected_target"]:
        lifecycle_state = DefenseLifecycleState.ANOMALY_OBSERVED.value
    elif not safety_checks["evidence_attribution_satisfied"]:
        lifecycle_state = DefenseLifecycleState.ANOMALY_OBSERVED.value
    elif is_dry_run or mode_upper in (DefenseMode.DRY_RUN.value, DefenseMode.AUTO_STAGE_ONLY.value):
        lifecycle_state = DefenseLifecycleState.BLOCK_PROPOSED.value
    elif not safety_checks["operator_approval_satisfied"]:
        lifecycle_state = DefenseLifecycleState.BLOCK_PROPOSED.value
    elif allowed_to_execute:
        lifecycle_state = DefenseLifecycleState.BLOCK_APPROVED.value
    else:
        lifecycle_state = DefenseLifecycleState.EVIDENCE_CORRELATED.value

    rollback_plan = {
        "reversible": True,
        "rollback_action": (
            "unblock_ip"
            if action_type in ("block_ip", "throttle_traffic", "redirect_traffic", "prioritize_traffic")
            else ("enable_port" if action_type == "disable_port" else "none")
        ),
        "target_device_id": target_device_id or "of:0000000000000001",
        "target_ip": target_ip,
        "target_port": target_port,
        "app_id": "org.onosproject.rest",
    }

    return SafetyGateVerdict(
        allowed_to_execute=allowed_to_execute,
        defense_mode=mode_upper,
        lifecycle_state=lifecycle_state,
        action_type=action_type,
        target_ip=target_ip,
        target_device_id=target_device_id,
        target_port=target_port,
        dry_run=is_dry_run,
        requires_manual_approval=requires_manual,
        rejection_reasons=rejection_reasons,
        safety_checks=safety_checks,
        rollback_plan=rollback_plan,
    )

