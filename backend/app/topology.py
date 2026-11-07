import os
import requests
from requests.auth import HTTPBasicAuth

try:
    from .database import get_setting_value
except ImportError:
    from database import get_setting_value


def _resolve_onos_session():
    controller_ip = get_setting_value("SDN Controller IP") or "127.0.0.1"
    base_url = os.environ.get("SDNFLOW_ONOS_URL") or f"http://{controller_ip}:8181/onos/v1"
    user = os.environ.get("SDNFLOW_ONOS_USER") or os.environ.get("ONOS_USER") or "onos"
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD") or os.environ.get("ONOS_PASSWORD") or "rocks"
    auth = HTTPBasicAuth(user, password) if (user or password) else None
    return base_url.rstrip("/"), auth


def fetch_devices():
    base_url, auth = _resolve_onos_session()
    devices_response = requests.get(f"{base_url}/devices", auth=auth, timeout=10)
    devices_response.raise_for_status()
    devices = devices_response.json().get("devices", [])

    processed_devices = []
    for device in devices:
        processed_devices.append(
            {
                "id": device.get("id"),
                "type": device.get("type"),
                "available": device.get("available"),
                "role": device.get("role"),
                "mfr": device.get("mfr"),
                "hw": device.get("hw"),
                "sw": device.get("sw"),
                "serial": device.get("serial"),
                "driver": device.get("driver"),
                "chassisId": device.get("chassisId"),
                "lastUpdate": device.get("lastUpdate"),
                "humanReadableLastUpdate": device.get("humanReadableLastUpdate"),
                "annotations": device.get("annotations", {}),
            }
        )
    return processed_devices


def fetch_links():
    base_url, auth = _resolve_onos_session()
    links_response = requests.get(f"{base_url}/links", auth=auth, timeout=10)
    links_response.raise_for_status()
    links = links_response.json().get("links", [])

    processed_links = []
    for link in links:
        processed_links.append(
            {
                "src": link.get("src"),
                "dst": link.get("dst"),
                "type": link.get("type"),
                "state": link.get("state"),
                "annotations": link.get("annotations", {}),
            }
        )
    return processed_links


def fetch_hosts():
    base_url, auth = _resolve_onos_session()
    hosts_response = requests.get(f"{base_url}/hosts", auth=auth, timeout=10)
    hosts_response.raise_for_status()
    hosts = hosts_response.json().get("hosts", [])

    processed_hosts = []
    for host in hosts:
        processed_hosts.append(
            {
                "id": host.get("id"),
                "mac": host.get("mac"),
                "vlan": host.get("vlan"),
                "ipAddresses": host.get("ipAddresses", []),
                "locations": host.get("locations", []),
            }
        )
    return processed_hosts


def get_topology_data():
    try:
        devices = fetch_devices()
        links = fetch_links()
        hosts = fetch_hosts()
        return {"devices": devices, "hosts": hosts, "links": links}
    except Exception as exc:
        raise RuntimeError(f"Error fetching topology data: {str(exc)}") from exc
