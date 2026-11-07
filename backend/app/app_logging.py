import os
import requests

try:
    from .database import get_setting_value, save_flows
except ImportError:
    from database import get_setting_value, save_flows


def _resolve_onos_flows_config():
    controller_ip = get_setting_value("SDN Controller IP") or "127.0.0.1"
    base_url = os.environ.get("SDNFLOW_ONOS_URL") or f"http://{controller_ip}:8181/onos/v1"
    user = os.environ.get("SDNFLOW_ONOS_USER") or os.environ.get("ONOS_USER") or "onos"
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD") or os.environ.get("ONOS_PASSWORD") or "rocks"
    return f"{base_url.rstrip('/')}/flows", (user, password)


def fetch_flows_from_onos():
    """Fetch flow information from the ONOS controller's REST API."""
    url, auth = _resolve_onos_flows_config()
    try:
        response = requests.get(url, auth=auth, timeout=10)
        if response.status_code == 200:
            return response.json().get("flows", [])
        raise Exception(
            f"Failed to fetch flows. Status code: {response.status_code}, Message: {response.text}"
        )
    except Exception as exc:
        raise Exception(f"Error fetching flows from ONOS: {exc}") from exc


def filter_flows(raw_flows):
    """Filter and format raw flow data retrieved from ONOS for saving into the database."""
    formatted_flows = []
    for flow in raw_flows:
        try:
            flow_id = flow.get("id", "Unknown")
            app_id = flow.get("appId", "Unknown")
            device_id = flow.get("deviceId", "Unknown")
            priority = flow.get("priority", 0)
            bandwidth = flow.get("bytes", 0)
            flow_duration = flow.get("life", 0)

            source_ip = "Unknown"
            destination_ip = "Unknown"
            protocol = "Unknown"
            eth_type = "Unknown"
            in_port = "Unknown"
            out_port = "Unknown"

            for criterion in flow.get("selector", {}).get("criteria", []):
                if criterion.get("type") == "IPV4_SRC":
                    source_ip = criterion.get("ip", "Unknown")
                elif criterion.get("type") == "IPV4_DST":
                    destination_ip = criterion.get("ip", "Unknown")
                elif criterion.get("type") == "ETH_TYPE":
                    eth_type = criterion.get("ethType", "Unknown")
                    if eth_type in ("0x800", "0x0800"):
                        protocol = "IPv4"
                    elif eth_type in ("0x86DD", "0x86dd"):
                        protocol = "IPv6"
                    else:
                        protocol = "Ethernet"
                elif criterion.get("type") == "IN_PORT":
                    in_port = f"Port {criterion.get('port', 'Unknown')}"
                elif criterion.get("type") == "OUT_PORT":
                    out_port = f"Port {criterion.get('port', 'Unknown')}"

            if destination_ip == "Unknown":
                for instruction in flow.get("treatment", {}).get("instructions", []):
                    if (
                        instruction.get("type") == "L3MODIFICATION"
                        and instruction.get("subtype") == "IPV4_DST"
                    ):
                        destination_ip = instruction.get("ip", "Unknown")

            formatted_flows.append(
                {
                    "id": flow_id,
                    "source_ip": source_ip,
                    "destination_ip": destination_ip,
                    "protocol": protocol,
                    "bandwidth": bandwidth,
                    "flow_duration": flow_duration,
                    "priority": priority,
                    "app_id": app_id,
                    "device_id": device_id,
                    "eth_type": eth_type,
                    "in_port": in_port,
                    "out_port": out_port,
                }
            )
        except Exception as exc:
            print(f"Error processing flow {flow.get('id', 'Unknown')}: {exc}")

    return formatted_flows


def log_flows_to_database():
    """Retrieve flow data from ONOS, filter it, and save it to the database."""
    raw_flows = fetch_flows_from_onos()
    formatted_flows = filter_flows(raw_flows)
    save_flows(formatted_flows)
    return formatted_flows
