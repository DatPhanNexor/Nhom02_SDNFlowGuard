import json
import os
from pathlib import Path
import requests

try:
    from .database import get_setting_value
except ImportError:
    from database import get_setting_value

INTENT_DIR = Path(__file__).resolve().parent / "generated_intents"


def _resolve_onos_intents_config():
    controller_ip = get_setting_value("SDN Controller IP") or "127.0.0.1"
    base_url = os.environ.get("SDNFLOW_ONOS_URL") or f"http://{controller_ip}:8181/onos/v1"
    user = os.environ.get("SDNFLOW_ONOS_USER") or os.environ.get("ONOS_USER") or "onos"
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD") or os.environ.get("ONOS_PASSWORD") or "rocks"
    return f"{base_url.rstrip('/')}/intents", (user, password)


def save_to_file(filename, data):
    """Saves JSON data to a file in the safe generated_intents directory."""
    INTENT_DIR.mkdir(parents=True, exist_ok=True)
    target = INTENT_DIR / Path(filename).name
    target.write_text(data, encoding="utf-8")
    return str(target)


def point_to_point_intent(
    source_ip,
    destination_ip,
    src_device,
    dst_device,
    src_port,
    dst_port,
    app_id="org.onosproject.cli",
    priority=200,
):
    """Create a Point-to-Point Intent to reroute traffic between two devices."""
    intent = {
        "type": "PointToPointIntent",
        "appId": app_id,
        "priority": priority,
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IPV4_SRC", "ip": f"{source_ip}/32"},
                {"type": "IPV4_DST", "ip": f"{destination_ip}/32"},
            ]
        },
        "ingressPoint": {"port": str(src_port), "device": src_device},
        "egressPoint": {"port": str(dst_port), "device": dst_device},
    }
    safe_name = f"intent_{str(src_device).replace(':', '_')}_{str(dst_device).replace(':', '_')}.json"
    saved_path = save_to_file(safe_name, json.dumps(intent, indent=4))

    url, auth = _resolve_onos_intents_config()
    response = requests.post(
        url,
        auth=auth,
        headers={"Content-Type": "application/json"},
        data=Path(saved_path).read_text(encoding="utf-8"),
        timeout=10,
    )
    return response.status_code == 201


def multipoint_to_singlepoint_intent(
    app_id,
    priority,
    ingress_points,
    egress_device,
    egress_port,
    source_ip=None,
    dest_ip=None,
    filename="multipoint_to_singlepoint_intent.json",
):
    intent = {
        "type": "MultipointToSinglepointIntent",
        "appId": app_id,
        "priority": priority,
        "ingressPoints": [
            {"device": point["device"], "port": point["port"]} for point in ingress_points
        ],
        "egressPoint": {"device": egress_device, "port": egress_port},
    }
    if source_ip and dest_ip:
        intent["selector"] = {
            "criteria": [
                {"type": "IPV4_SRC", "ip": f"{source_ip}/32"},
                {"type": "IPV4_DST", "ip": f"{dest_ip}/32"},
            ]
        }
    intent_json = json.dumps(intent, indent=4)
    save_to_file(filename, intent_json)
    return intent_json


def broadcast_intent(
    app_id,
    priority,
    ingress_device,
    ingress_port,
    broadcast_group,
    filename="broadcast_intent.json",
):
    intent = {
        "type": "BroadcastIntent",
        "appId": app_id,
        "priority": priority,
        "ingressPoint": {"device": ingress_device, "port": ingress_port},
        "broadcastGroup": [
            {"device": device["device"], "port": device["port"]} for device in broadcast_group
        ],
    }
    intent_json = json.dumps(intent, indent=4)
    save_to_file(filename, intent_json)
    return intent_json


def vlan_intent(
    app_id,
    priority,
    ingress_device,
    ingress_port,
    vlan_id,
    treatment_vlan_id=None,
    filename="vlan_intent.json",
):
    intent = {
        "type": "VlanIntent",
        "appId": app_id,
        "priority": priority,
        "ingressPoint": {"device": ingress_device, "port": ingress_port},
        "selector": {"criteria": [{"type": "VLAN_VID", "vlanId": vlan_id}]},
    }
    if treatment_vlan_id:
        intent["treatment"] = {
            "instructions": [{"type": "VLAN_PUSH", "vlanId": treatment_vlan_id}]
        }
    intent_json = json.dumps(intent, indent=4)
    save_to_file(filename, intent_json)
    return intent_json
