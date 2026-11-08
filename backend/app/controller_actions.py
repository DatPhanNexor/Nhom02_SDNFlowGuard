from collections import defaultdict
from heapq import heappop, heappush
import json
import os
from pathlib import Path
import sys
import time
import requests
from requests.auth import HTTPBasicAuth

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sdnflowguard.domain.policies.safety_gate import evaluate_safety_gate  # noqa: E402
from sdnflowguard.infrastructure.configuration.settings import AppSettings  # noqa: E402
from sdnflowguard.observability.structured_logger import generate_request_id  # noqa: E402

try:
    from .database import get_setting_value, record_action
    from .generator import point_to_point_intent
    from .topology import get_topology_data
except ImportError:
    from database import get_setting_value, record_action
    from generator import point_to_point_intent
    from topology import get_topology_data

CONFIG_DIRECTORY = str(Path(__file__).resolve().parent / "generated_intents")


def _resolve_onos_api():
    settings = AppSettings.from_env()
    controller_ip = get_setting_value("SDN Controller IP") or "127.0.0.1"
    elk_ip = get_setting_value("ELK IP Address") or "127.0.0.1"
    base_url = os.environ.get("SDNFLOW_ONOS_URL") or f"http://{controller_ip}:8181/onos/v1"
    user = settings.onos_user or os.environ.get("ONOS_USER") or "onos"
    password = settings.onos_password or os.environ.get("ONOS_PASSWORD") or "rocks"
    auth = HTTPBasicAuth(user, password) if (user or password) else None
    return {
        "settings": settings,
        "controller_ip": controller_ip,
        "elk_ip": elk_ip,
        "base_url": base_url.rstrip("/"),
        "auth": auth,
    }


def _strip_cidr(ip_val):
    if not ip_val:
        return None
    return str(ip_val).split("/")[0].strip()


def log_action(action_type, reason, source_ip, admin_or_automated="Admin"):
    """Utility function to log actions in the database."""
    return record_action(
        action_type=action_type,
        reason=reason,
        source_ip=source_ip or "N/A",
        admin_or_automated=admin_or_automated,
    )


def is_valid_ip(ip):
    """Validate IPv4 address with CIDR suffix (e.g. 10.0.0.1/32)."""
    try:
        if not ip or "/" not in str(ip):
            return False
        base_ip, subnet = str(ip).split("/")
        parts = base_ip.split(".")
        if len(parts) != 4 or not all(0 <= int(part) <= 255 for part in parts):
            return False
        subnet_int = int(subnet)
        return 0 <= subnet_int <= 32
    except (ValueError, IndexError):
        return False


def _evaluate_action_gate(
    action_type,
    target_ip,
    dst_ip=None,
    admin_or_automated="Admin",
    dry_run=None,
    test_only=False,
    operator_authenticated=None,
):
    api_info = _resolve_onos_api()
    is_manual = str(admin_or_automated).lower() == "admin"
    if operator_authenticated is None:
        configured_key = getattr(api_info.get("settings"), "api_key", None)
        if configured_key:
            operator_authenticated = False
        else:
            operator_authenticated = is_manual
    verdict = evaluate_safety_gate(
        action_type=action_type,
        defense_mode=api_info["settings"].defense_mode,
        target_ip=target_ip,
        dst_ip=dst_ip,
        test_only=test_only,
        manual_operator_override=is_manual,
        operator_approved=is_manual,
        operator_authenticated=operator_authenticated,
        allowlist_ips=api_info["settings"].allowlist_ips,
        controller_ip=api_info["controller_ip"],
        elk_ip=api_info["elk_ip"],
        explicit_dry_run=dry_run,
    )
    return verdict, api_info


def create_acl_rule(
    src_ip=None,
    dst_ip=None,
    src_mac=None,
    dst_mac=None,
    vlan_id=None,
    eth_type="0x0800",
    ip_proto="TCP",
    src_port=None,
    dst_port=None,
    action="ALLOW",
    dry_run=None,
):
    if src_ip and not is_valid_ip(src_ip):
        return {"status": "VALIDATION_ERROR", "error": f"Invalid source IP address: {src_ip}"}
    if dst_ip and not is_valid_ip(dst_ip):
        return {"status": "VALIDATION_ERROR", "error": f"Invalid destination IP address: {dst_ip}"}
    if action not in ["ALLOW", "DENY"]:
        return {"status": "VALIDATION_ERROR", "error": f"Invalid action: {action}"}

    acl_rule = {"action": action}
    if src_ip:
        acl_rule["srcIp"] = src_ip
    if dst_ip:
        acl_rule["dstIp"] = dst_ip
    if src_mac:
        acl_rule["srcMac"] = src_mac
    if dst_mac:
        acl_rule["dstMac"] = dst_mac
    if vlan_id:
        acl_rule["vlanId"] = vlan_id
    if eth_type:
        acl_rule["ethType"] = eth_type
    if ip_proto:
        acl_rule["ipProto"] = ip_proto
    if src_port:
        acl_rule["srcTpPort"] = src_port
    if dst_port:
        acl_rule["dstTpPort"] = dst_port

    criteria = [{"type": "ETH_TYPE", "ethType": eth_type or "0x0800"}]
    if src_ip:
        criteria.append({"type": "IPV4_SRC", "ip": src_ip})
    if dst_ip:
        criteria.append({"type": "IPV4_DST", "ip": dst_ip})
    flow_rule_preview = {
        "priority": 40010,
        "timeout": 300,
        "isPermanent": False,
        "deviceId": "of:0000000000000001",
        "selector": {"criteria": criteria},
        "treatment": {
            "instructions": [] if action == "DENY" else [{"type": "OUTPUT", "port": "CONTROLLER"}]
        },
    }

    verdict, api_info = _evaluate_action_gate(
        "block_ip" if action == "DENY" else "allow_ip",
        target_ip=src_ip,
        dst_ip=dst_ip,
        dry_run=dry_run,
    )
    if not verdict.safety_checks["valid_and_unprotected_target"]:
        return {
            "request_id": generate_request_id(),
            "status": "REJECTED_BY_SAFETY_GATE",
            "executed": False,
            "dry_run": verdict.dry_run,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
            "acl_rule_preview": acl_rule,
            "flow_rule_preview": flow_rule_preview,
        }

    if verdict.dry_run or not verdict.allowed_to_execute:
        return {
            "request_id": generate_request_id(),
            "status": "DRY_RUN_SIMULATED",
            "executed": False,
            "dry_run": True,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
            "acl_rule_preview": acl_rule,
            "flow_rule_preview": flow_rule_preview,
        }

    url = f"{api_info['base_url']}/acl/rules"
    try:
        requests.post(
            f"{api_info['base_url']}/applications/org.onosproject.acl/active",
            auth=api_info["auth"],
            timeout=5,
        )
        response = requests.post(url, json=acl_rule, auth=api_info["auth"], timeout=10)
        return {
            "request_id": generate_request_id(),
            "status": "RULE_APPLIED" if response.status_code in (200, 201) else "EXECUTION_FAILED",
            "executed": response.status_code in (200, 201),
            "dry_run": False,
            "defense_mode": verdict.defense_mode,
            "acl_rule": acl_rule,
            "flow_rule_preview": flow_rule_preview,
        }
    except requests.exceptions.RequestException as exc:
        return {
            "request_id": generate_request_id(),
            "status": "EXECUTION_FAILED",
            "executed": False,
            "dry_run": False,
            "error": str(exc),
        }


def block_ip(
    src_ip=None,
    dst_ip=None,
    src_mac=None,
    dst_mac=None,
    vlan_id=None,
    eth_type=None,
    ip_proto=None,
    src_port=None,
    dst_port=None,
    admin_or_automated="Admin",
    dry_run=None,
    test_only=False,
    operator_authenticated=None,
):
    if src_ip and "/" not in str(src_ip):
        src_ip = f"{src_ip}/32"
    if dst_ip and "/" not in str(dst_ip):
        dst_ip = f"{dst_ip}/32"

    verdict, _ = _evaluate_action_gate(
        "block_ip",
        target_ip=src_ip,
        dst_ip=dst_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
        test_only=test_only,
        operator_authenticated=operator_authenticated,
    )

    if not verdict.safety_checks["valid_and_unprotected_target"] or not verdict.safety_checks["not_test_only_alert"]:
        return {
            "request_id": generate_request_id(),
            "status": "REJECTED_BY_SAFETY_GATE",
            "executed": False,
            "dry_run": verdict.dry_run,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
        }

    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Block{mode_tag}",
        reason=f"Blocked traffic for {src_ip} to {dst_ip}.{mode_tag}",
        source_ip=src_ip or dst_ip or "N/A",
        admin_or_automated=admin_or_automated,
    )
    return create_acl_rule(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        vlan_id=vlan_id,
        eth_type=eth_type or "0x0800",
        src_port=src_port,
        dst_port=dst_port,
        ip_proto=ip_proto or "TCP",
        action="DENY",
        dry_run=verdict.dry_run,
    )


def allow_ip(
    src_ip=None,
    dst_ip=None,
    src_mac=None,
    dst_mac=None,
    vlan_id=None,
    eth_type=None,
    ip_proto=None,
    src_port=None,
    dst_port=None,
    admin_or_automated="Admin",
    dry_run=None,
):
    if src_ip and "/" not in str(src_ip):
        src_ip = f"{src_ip}/32"
    if dst_ip and "/" not in str(dst_ip):
        dst_ip = f"{dst_ip}/32"

    verdict, _ = _evaluate_action_gate(
        "unblock_ip",
        target_ip=src_ip,
        dst_ip=dst_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
    )
    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Allow{mode_tag}",
        reason=f"Allow traffic from {src_ip} to {dst_ip}.{mode_tag}",
        source_ip=src_ip or dst_ip or "N/A",
        admin_or_automated=admin_or_automated,
    )
    return create_acl_rule(
        src_ip=src_ip,
        dst_ip=dst_ip,
        src_mac=src_mac,
        dst_mac=dst_mac,
        vlan_id=vlan_id,
        eth_type=eth_type or "0x0800",
        src_port=src_port,
        dst_port=dst_port,
        ip_proto=ip_proto or "TCP",
        action="ALLOW",
        dry_run=verdict.dry_run,
    )


def list_acl_rules():
    """Fetch ACL rules from ONOS controller, returning list of rules, or None on controller error."""
    api_info = _resolve_onos_api()
    try:
        url = f"{api_info['base_url']}/acl/rules"
        response = requests.get(url, auth=api_info["auth"], timeout=10)
        if response.status_code == 200:
            return response.json().get("aclRules", [])
        return None
    except requests.exceptions.RequestException:
        return None


def fetch_acl_rules():
    """Fetch ACL rules from ONOS controller, returning (rules_list, success, error_message)."""
    rules = list_acl_rules()
    if rules is not None:
        return rules, True, None
    return [], False, "ONOS controller unavailable or returned error"


def unblock_ip(
    src_ip=None,
    dst_ip=None,
    src_port=None,
    dst_port=None,
    prefix_length="32",
    admin_or_automated="Admin",
    dry_run=None,
    return_structured=False,
):
    if src_ip and "/" not in str(src_ip):
        src_ip = f"{src_ip}/{prefix_length}"
    if dst_ip and "/" not in str(dst_ip):
        dst_ip = f"{dst_ip}/{prefix_length}"

    if src_ip and not is_valid_ip(src_ip):
        err = f"Invalid source IP address: {src_ip}"
        if return_structured:
            return {
                "request_id": generate_request_id(),
                "status": "VALIDATION_ERROR",
                "executed": False,
                "dry_run": bool(dry_run),
                "error": err,
                "message": err,
            }
        return err
    if dst_ip and not is_valid_ip(dst_ip):
        err = f"Invalid destination IP address: {dst_ip}"
        if return_structured:
            return {
                "request_id": generate_request_id(),
                "status": "VALIDATION_ERROR",
                "executed": False,
                "dry_run": bool(dry_run),
                "error": err,
                "message": err,
            }
        return err

    clean_target = _strip_cidr(src_ip or dst_ip)

    verdict, api_info = _evaluate_action_gate(
        "unblock_ip",
        target_ip=src_ip,
        dst_ip=dst_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
    )
    if not verdict.safety_checks["valid_and_unprotected_target"]:
        err_msg = "Unblock rejected by Safety Gate (target IP is protected)"
        if return_structured:
            return {
                "request_id": generate_request_id(),
                "status": "REJECTED_BY_SAFETY_GATE",
                "target_ip": clean_target,
                "executed": False,
                "dry_run": verdict.dry_run,
                "defense_mode": verdict.defense_mode,
                "safety_verdict": verdict.to_dict(),
                "message": err_msg,
            }
        return err_msg

    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Unblock{mode_tag}",
        reason=f"Unblock traffic from {src_ip} to {dst_ip}.{mode_tag}",
        source_ip=src_ip or dst_ip or "N/A",
        admin_or_automated=admin_or_automated,
    )

    if verdict.dry_run or not verdict.allowed_to_execute:
        msg = f"[DRY RUN] Simulated unblock for IP {src_ip or dst_ip}"
        if return_structured:
            return {
                "request_id": generate_request_id(),
                "status": "ROLLBACK_SIMULATED",
                "target_ip": clean_target,
                "executed": False,
                "dry_run": True,
                "rule_id": None,
                "controller_status": None,
                "verification_result": "SIMULATED",
                "message": msg,
            }
        return msg

    acl_rules = list_acl_rules()
    if acl_rules is None:
        err_msg = "Cannot communicate with ONOS controller (controller unavailable)"
        if return_structured:
            return {
                "request_id": generate_request_id(),
                "status": "CONTROLLER_UNAVAILABLE",
                "target_ip": clean_target,
                "executed": False,
                "dry_run": False,
                "rule_id": None,
                "controller_status": None,
                "verification_result": "FAILED_CONTROLLER_UNREACHABLE",
                "error": err_msg,
                "message": err_msg,
            }
        return err_msg

    for rule in acl_rules:
        if isinstance(rule, dict):
            rule_src_ip = rule.get("srcIp", "").strip()
            rule_dst_ip = rule.get("dstIp", "").strip()
            if (src_ip and rule_src_ip == src_ip) or (dst_ip and rule_dst_ip == dst_ip):
                rule_id = rule.get("id")
                delete_url = f"{api_info['base_url']}/acl/rules/{rule_id}"
                try:
                    response = requests.delete(delete_url, auth=api_info["auth"], timeout=10)
                    if response.status_code in (200, 204):
                        # Verify rule removal from ONOS
                        rem_rules = list_acl_rules()
                        still_there = any(r.get("id") == rule_id for r in rem_rules if isinstance(r, dict))
                        v_result = "ROLLBACK_VERIFIED" if not still_there else "DELETE_REQUEST_ACCEPTED"
                        msg = f"Successfully unblocked traffic for IP: {src_ip or dst_ip}"
                        if return_structured:
                            return {
                                "request_id": generate_request_id(),
                                "status": "ROLLBACK_COMPLETED",
                                "target_ip": clean_target,
                                "executed": True,
                                "dry_run": False,
                                "rule_id": rule_id,
                                "controller_status": response.status_code,
                                "verification_result": v_result,
                                "message": msg,
                            }
                        return msg
                    else:
                        fail_msg = f"ONOS failed to delete rule {rule_id}: HTTP {response.status_code}"
                        if return_structured:
                            return {
                                "request_id": generate_request_id(),
                                "status": "ROLLBACK_FAILED",
                                "target_ip": clean_target,
                                "executed": False,
                                "dry_run": False,
                                "rule_id": rule_id,
                                "controller_status": response.status_code,
                                "verification_result": "EXECUTION_FAILED",
                                "error": fail_msg,
                                "message": fail_msg,
                            }
                        return fail_msg
                except requests.exceptions.RequestException as exc:
                    if return_structured:
                        return {
                            "request_id": generate_request_id(),
                            "status": "ROLLBACK_FAILED",
                            "target_ip": clean_target,
                            "executed": False,
                            "dry_run": False,
                            "rule_id": rule_id,
                            "controller_status": None,
                            "verification_result": "EXECUTION_FAILED",
                            "error": str(exc),
                            "message": f"Failed to delete rule {rule_id}: {exc}",
                        }
                    return f"Failed to delete rule {rule_id}: {exc}"

    msg = f"No ACL rule found for IP {src_ip or dst_ip}"
    if return_structured:
        return {
            "request_id": generate_request_id(),
            "status": "ROLLBACK_SKIPPED_NO_RULE",
            "target_ip": clean_target,
            "executed": False,
            "dry_run": False,
            "rule_id": None,
            "controller_status": None,
            "verification_result": "RULE_NOT_FOUND",
            "message": msg,
        }
    return msg


def redirect_traffic(
    src_ip,
    dest_ip,
    ingress_port,
    egress_port,
    device_id,
    config_name="redirect_intent",
    admin_or_automated="Admin",
    dry_run=None,
):
    if src_ip and "/" not in str(src_ip):
        src_ip = f"{src_ip}/32"
    if dest_ip and "/" not in str(dest_ip):
        dest_ip = f"{dest_ip}/32"
    if not is_valid_ip(src_ip) or not is_valid_ip(dest_ip):
        return {"status": "VALIDATION_ERROR", "error": "Invalid source or destination IP"}

    dest_ip_without_cidr = dest_ip.split("/")[0]
    verdict, api_info = _evaluate_action_gate(
        "redirect_traffic",
        src_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
    )
    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Redirect{mode_tag}",
        reason=f"Redirected traffic from {src_ip} to {dest_ip}.{mode_tag}",
        source_ip=src_ip,
        admin_or_automated=admin_or_automated,
    )

    intent = {
        "type": "PointToPointIntent",
        "priority": 40000,
        "appId": "org.onosproject.cli",
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IPV4_SRC", "ip": src_ip},
            ]
        },
        "treatment": {
            "instructions": [
                {"type": "L3MODIFICATION", "subtype": "IPV4_DST", "ip": dest_ip_without_cidr}
            ]
        },
        "ingressPoint": {"port": ingress_port, "device": device_id},
        "egressPoint": {"port": egress_port, "device": device_id},
    }

    if verdict.dry_run or not verdict.allowed_to_execute:
        return {
            "request_id": generate_request_id(),
            "status": "DRY_RUN_SIMULATED",
            "executed": False,
            "dry_run": True,
            "defense_mode": verdict.defense_mode,
            "intent_preview": intent,
        }

    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)
    file_path = os.path.join(CONFIG_DIRECTORY, f"{config_name}.json")
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(intent, json_file, indent=4)

    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{api_info['base_url']}/intents",
        headers=headers,
        data=json.dumps(intent),
        auth=api_info["auth"],
        timeout=10,
    )
    return {
        "request_id": generate_request_id(),
        "status": "RULE_APPLIED" if response.status_code == 201 else "EXECUTION_FAILED",
        "executed": response.status_code == 201,
        "dry_run": False,
    }


def rate_limit_for_host(host_ip, rate_limit_bps, admin_or_automated="Admin", dry_run=None, test_only=False, operator_authenticated=None):
    verdict, api_info = _evaluate_action_gate(
        "throttle_traffic",
        host_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
        test_only=test_only,
        operator_authenticated=operator_authenticated,
    )
    if not verdict.safety_checks["valid_and_unprotected_target"] or not verdict.safety_checks["not_test_only_alert"]:
        return {
            "request_id": generate_request_id(),
            "status": "REJECTED_BY_SAFETY_GATE",
            "executed": False,
            "dry_run": verdict.dry_run,
            "safety_verdict": verdict.to_dict(),
        }

    try:
        rate_bps_int = int(rate_limit_bps)
        if rate_bps_int <= 0:
            return {
                "request_id": generate_request_id(),
                "status": "VALIDATION_ERROR",
                "executed": False,
                "error": f"rateLimitBps must be a positive integer, got: {rate_limit_bps}",
            }
    except (ValueError, TypeError):
        return {
            "request_id": generate_request_id(),
            "status": "VALIDATION_ERROR",
            "executed": False,
            "error": f"Invalid rateLimitBps: {rate_limit_bps}",
        }

    # Unit conversion: ONOS Meter.Unit uses "KB_PER_SEC" which represents Kilo-bits per second (kbps),
    # matching OpenFlow 1.3 specification (OFPMC_KBPS: 1 kbps = 1000 bps).
    # Note: In ONOS Meter.Unit, "KB_PER_SEC" means kilobits/second, NOT kilobytes/second.
    # Convert input bps to kbps (KB_PER_SEC) with a 1 kbps minimum lower bound.
    rate_kb_per_sec = max(1, int(round(rate_bps_int / 1000.0)))

    if verdict.dry_run or not verdict.allowed_to_execute:
        log_action(
            action_type="Rate Limit [DRY_RUN]",
            reason=f"Simulated rate limit for {host_ip} to {rate_limit_bps} bps ({rate_kb_per_sec} kbps / KB_PER_SEC).",
            source_ip=host_ip,
            admin_or_automated=admin_or_automated,
        )
        return {
            "request_id": generate_request_id(),
            "status": "DRY_RUN_SIMULATED",
            "executed": False,
            "dry_run": True,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
            "rate_limit_bps": rate_bps_int,
            "rate_kb_per_sec": rate_kb_per_sec,
        }

    topology_data = get_topology_data()
    hosts = topology_data.get("hosts", [])
    target_host = next((host for host in hosts if host_ip in host.get("ipAddresses", [])), None)
    if not target_host:
        return {"status": "HOST_NOT_FOUND", "executed": False}

    host_mac = target_host.get("mac")
    locations = target_host.get("locations", [])
    if not host_mac or not locations:
        return {"status": "INCOMPLETE_HOST_LOCATION", "executed": False}

    closest_location = locations[0]
    device_id = closest_location.get("elementId")
    inbound_port = closest_location.get("port")

    log_action(
        action_type="Rate Limit",
        reason=f"Rate limited {host_ip} ({host_mac}) to {rate_limit_bps} bps ({rate_kb_per_sec} kbps / KB_PER_SEC).",
        source_ip=host_ip,
        admin_or_automated=admin_or_automated,
    )

    meter_id = str(int(time.time()))
    meter_config = {
        "deviceId": device_id,
        "meterId": meter_id,
        "unit": "KB_PER_SEC",
        "bands": [{"type": "DROP", "rate": rate_kb_per_sec, "burstSize": max(100, int(rate_kb_per_sec // 2))}],
    }
    meter_url = f"{api_info['base_url']}/meters/{device_id}"
    meter_response = requests.post(meter_url, json=meter_config, auth=api_info["auth"], timeout=10)
    if meter_response.status_code != 201:
        return {"status": "EXECUTION_FAILED", "executed": False, "error": meter_response.text}

    meters_response = requests.get(meter_url, auth=api_info["auth"], timeout=10)
    if meters_response.status_code == 200:
        meters = meters_response.json().get("meters", [])
        latest_meter = next(
            (m for m in meters if m.get("bands", [{}])[0].get("rate") == rate_kb_per_sec),
            None,
        )
        if latest_meter:
            meter_id = latest_meter["id"]
            flow_rule = {
                "priority": 41000,
                "timeout": 0,
                "isPermanent": True,
                "deviceId": device_id,
                "treatment": {
                    "instructions": [
                        {"type": "METER", "meterId": meter_id},
                        {"type": "OUTPUT", "port": inbound_port},
                    ]
                },
                "selector": {
                    "criteria": [
                        {"type": "ETH_TYPE", "ethType": "0x0800"},
                        {"type": "ETH_DST", "mac": host_mac},
                    ]
                },
            }
            flow_url = f"{api_info['base_url']}/flows/{device_id}"
            flow_response = requests.post(flow_url, json=flow_rule, auth=api_info["auth"], timeout=10)
            return {
                "request_id": generate_request_id(),
                "status": "RULE_APPLIED" if flow_response.status_code == 201 else "EXECUTION_FAILED",
                "executed": flow_response.status_code == 201,
                "dry_run": False,
            }
    return {"status": "EXECUTION_FAILED", "executed": False}


def calculate_shortest_path(src_device_id, dst_device_id, links):
    """Calculate the shortest path between two devices using Dijkstra's algorithm."""
    graph = defaultdict(list)
    for link in links:
        src = link["src"]
        dst = link["dst"]
        latency = float(link.get("annotations", {}).get("latency", 1))
        graph[src["device"]].append((latency, dst["device"], src["port"], dst["port"]))
        graph[dst["device"]].append((latency, src["device"], dst["port"], src["port"]))

    queue = [(0, src_device_id, [])]
    visited = set()
    while queue:
        latency, device, path = heappop(queue)
        if device in visited:
            continue
        visited.add(device)
        path = path + [device]
        if device == dst_device_id:
            return path
        for next_latency, next_device, _, _ in graph[device]:
            if next_device not in visited:
                heappush(queue, (latency + next_latency, next_device, path))
    return []


def create_point_to_point_intents(
    source_ip,
    destination_ip,
    src_device,
    dst_device,
    src_port,
    dst_port,
    app_id="org.onosproject.cli",
    priority=200,
):
    return point_to_point_intent(
        source_ip=source_ip,
        destination_ip=destination_ip,
        src_device=src_device,
        dst_device=dst_device,
        src_port=src_port,
        dst_port=dst_port,
        app_id=app_id,
        priority=priority,
    )


def redirect_traffic_full(source_ip, honeypot_ip, admin_or_automated="Admin", dry_run=None, test_only=False):
    verdict, _ = _evaluate_action_gate(
        "redirect_traffic",
        source_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
        test_only=test_only,
    )
    if not verdict.safety_checks["valid_and_unprotected_target"] or not verdict.safety_checks["not_test_only_alert"]:
        return {
            "request_id": generate_request_id(),
            "status": "REJECTED_BY_SAFETY_GATE",
            "executed": False,
            "dry_run": verdict.dry_run,
            "safety_verdict": verdict.to_dict(),
        }

    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Redirect{mode_tag}",
        reason=f"Redirected traffic from {source_ip} to {honeypot_ip}.{mode_tag}",
        source_ip=source_ip,
        admin_or_automated=admin_or_automated,
    )

    if verdict.dry_run or not verdict.allowed_to_execute:
        return {
            "request_id": generate_request_id(),
            "status": "DRY_RUN_SIMULATED",
            "executed": False,
            "dry_run": True,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
        }

    topology_data = get_topology_data()
    links = topology_data.get("links", [])
    hosts = topology_data.get("hosts", [])
    source_host = next((host for host in hosts if source_ip in host.get("ipAddresses", [])), None)
    honeypot_host = next((host for host in hosts if honeypot_ip in host.get("ipAddresses", [])), None)
    if not source_host or not honeypot_host:
        return {"status": "HOST_NOT_FOUND", "executed": False}

    src_location = source_host["locations"][0]
    dst_location = honeypot_host["locations"][0]
    src_device_id = src_location["elementId"]
    src_port = src_location["port"]
    dst_device_id = dst_location["elementId"]
    dst_port = dst_location["port"]

    path = calculate_shortest_path(src_device_id, dst_device_id, links)
    if not path:
        return {"status": "NO_PATH_FOUND", "executed": False}

    applied = create_point_to_point_intents(
        source_ip=source_ip,
        destination_ip=honeypot_ip,
        src_device=src_device_id,
        dst_device=dst_device_id,
        src_port=src_port,
        dst_port=dst_port,
    )
    return {
        "request_id": generate_request_id(),
        "status": "RULE_APPLIED" if applied else "EXECUTION_FAILED",
        "executed": bool(applied),
        "dry_run": False,
    }


def redirect_to_intermediate_ovs(source_ip, ovs_id, admin_or_automated="Admin", dry_run=None, test_only=False):
    verdict, api_info = _evaluate_action_gate(
        "redirect_traffic",
        source_ip,
        admin_or_automated=admin_or_automated,
        dry_run=dry_run,
        test_only=test_only,
    )
    if not verdict.safety_checks["valid_and_unprotected_target"] or not verdict.safety_checks["not_test_only_alert"]:
        return {
            "request_id": generate_request_id(),
            "status": "REJECTED_BY_SAFETY_GATE",
            "executed": False,
            "dry_run": verdict.dry_run,
            "safety_verdict": verdict.to_dict(),
        }

    mode_tag = " [DRY_RUN]" if verdict.dry_run else ""
    log_action(
        action_type=f"Redirect{mode_tag}",
        reason=f"Redirected traffic from {source_ip} to intermediate switch {ovs_id}.{mode_tag}",
        source_ip=source_ip,
        admin_or_automated=admin_or_automated,
    )

    if verdict.dry_run or not verdict.allowed_to_execute:
        return {
            "request_id": generate_request_id(),
            "status": "DRY_RUN_SIMULATED",
            "executed": False,
            "dry_run": True,
            "defense_mode": verdict.defense_mode,
            "safety_verdict": verdict.to_dict(),
        }

    topology_data = get_topology_data()
    devices = topology_data.get("devices", [])
    links = topology_data.get("links", [])
    hosts = topology_data.get("hosts", [])

    source_host = next((host for host in hosts if source_ip in host.get("ipAddresses", [])), None)
    intermediate_switch = next((device for device in devices if device["id"] == ovs_id), None)
    if not source_host or not intermediate_switch:
        return {"status": "TOPOLOGY_ENTITY_NOT_FOUND", "executed": False}

    source_location = source_host.get("locations", [])[0]
    src_device_id = source_location.get("elementId")
    ingress_port = source_location.get("port")
    intermediate_device_id = intermediate_switch["id"]

    link_to_intermediate = next(
        (
            l
            for l in links
            if l["src"]["device"] == src_device_id and l["dst"]["device"] == intermediate_device_id
        ),
        None,
    )
    if not link_to_intermediate:
        return {"status": "NO_DIRECT_LINK", "executed": False}

    egress_port = link_to_intermediate["src"]["port"]
    intent = {
        "type": "PointToPointIntent",
        "appId": "org.onosproject.cli",
        "priority": 200,
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IPV4_SRC", "ip": f"{source_ip}/32"},
            ]
        },
        "ingressPoint": {"port": str(ingress_port), "device": src_device_id},
        "egressPoint": {"port": str(egress_port), "device": src_device_id},
    }
    headers = {"Content-Type": "application/json"}
    url = f"{api_info['base_url']}/intents"
    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(intent),
        auth=api_info["auth"],
        timeout=10,
    )
    return {
        "request_id": generate_request_id(),
        "status": "RULE_APPLIED" if response.status_code == 201 else "EXECUTION_FAILED",
        "executed": response.status_code == 201,
        "dry_run": False,
    }
