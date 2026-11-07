import os
import socket
import requests


def is_host_alive(ip, port=None):
    """Check if a host is reachable. Optionally check if a specific TCP port is open."""
    try:
        if port:
            with socket.create_connection((ip, int(port)), timeout=3):
                return True
        socket.gethostbyname(ip)
        return True
    except (socket.timeout, socket.error, ValueError):
        return False


def check_elk_status(ip):
    """Check if the ELK (Elasticsearch) service is running."""
    user = os.environ.get("SDNFLOW_ELK_USER") or ""
    password = os.environ.get("SDNFLOW_ELK_PASSWORD") or ""
    auth = (user, password) if (user or password) else None
    url = os.environ.get("SDNFLOW_ELK_URL") or f"http://{ip or '127.0.0.1'}:9200"
    try:
        response = requests.get(url, timeout=3, auth=auth)
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_onos_status(ip):
    """Check if the ONOS SDN Controller is running."""
    user = os.environ.get("SDNFLOW_ONOS_USER") or os.environ.get("ONOS_USER") or "onos"
    password = os.environ.get("SDNFLOW_ONOS_PASSWORD") or os.environ.get("ONOS_PASSWORD") or "rocks"
    auth = (user, password) if (user or password) else None
    base_url = (os.environ.get("SDNFLOW_ONOS_URL") or f"http://{ip or '127.0.0.1'}:8181/onos/v1").rstrip("/")
    try:
        response = requests.get(
            f"{base_url}/devices",
            timeout=3,
            auth=auth,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def check_kibana_status(ip=None):
    """Check if Kibana is running and healthy."""
    target_host = ip
    if not target_host or target_host in ("127.0.0.1", "localhost"):
        target_host = os.environ.get("SDNFLOW_KIBANA_HOST") or "kibana"
    url = os.environ.get("SDNFLOW_KIBANA_URL") or f"http://{target_host}:5601/api/status"
    try:
        response = requests.get(url, timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        try:
            fallback = requests.get("http://127.0.0.1:5601/api/status", timeout=2)
            return fallback.status_code == 200
        except requests.RequestException:
            return False


def check_logstash_status(host=None, port=None):
    """Check if Logstash HTTP ingestion receiver is running."""
    h = host or os.environ.get("SDNFLOW_LOGSTASH_HOST") or "logstash"
    p = port or os.environ.get("SDNFLOW_LOGSTASH_PORT") or 8080
    try:
        response = requests.get(f"http://{h}:{p}", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        try:
            fallback = requests.get("http://127.0.0.1:18080", timeout=2)
            return fallback.status_code == 200
        except requests.RequestException:
            return False


def check_openflow_status(host=None, port=6653):
    """Check if ONOS OpenFlow 1.3 TCP port 6653 is listening."""
    target_host = host
    if not target_host or target_host in ("127.0.0.1", "localhost"):
        onos_url = os.environ.get("SDNFLOW_ONOS_URL", "")
        if "onos" in onos_url:
            target_host = "onos"
        else:
            target_host = os.environ.get("SDNFLOW_ONOS_HOST") or "onos"
    try:
        with socket.create_connection((target_host, int(port)), timeout=3):
            return True
    except (socket.timeout, socket.error, ValueError):
        try:
            with socket.create_connection(("127.0.0.1", int(port)), timeout=2):
                return True
        except (socket.timeout, socket.error, ValueError):
            return False


def get_logstash_pipeline_stats(host=None, port=9600):
    """Retrieve verified Logstash pipeline metrics from internal Monitoring API."""
    target_host = host or os.environ.get("SDNFLOW_LOGSTASH_HOST") or "logstash"
    url = f"http://{target_host}:{port}/_node/stats/pipelines"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            main_pipe = data.get("pipelines", {}).get("main", {})
            events = main_pipe.get("events", {})
            plugins = main_pipe.get("plugins", {})
            outputs = plugins.get("outputs", [{}])
            out_success = 0
            if outputs and len(outputs) > 0:
                out_success = outputs[0].get("documents", {}).get("successes", 0)

            flow = main_pipe.get("flow", {})
            backpressure = flow.get("queue_backpressure", {}).get("current", 0.0)

            return {
                "status": data.get("status", "green"),
                "pipeline_id": "main",
                "events_received": events.get("in", 0),
                "events_filtered": events.get("filtered", 0),
                "events_emitted": events.get("out", 0),
                "documents_indexed": out_success,
                "queue_backpressure": round(float(backpressure), 4),
                "reload_failures": main_pipe.get("reloads", {}).get("failures", 0),
                "operational": True,
            }
    except requests.RequestException:
        pass

    return {
        "status": "UP" if check_logstash_status() else "DOWN",
        "pipeline_id": "main",
        "events_received": 0,
        "events_filtered": 0,
        "events_emitted": 0,
        "documents_indexed": 0,
        "queue_backpressure": 0.0,
        "reload_failures": 0,
        "operational": check_logstash_status(),
    }


def get_service_status(elk_ip, onos_ip):
    """Retrieve the status of ELK, ONOS, Kibana, Logstash, and OpenFlow."""
    elk_status = check_elk_status(elk_ip or "127.0.0.1")
    onos_status = check_onos_status(onos_ip or "127.0.0.1")
    kibana_status = check_kibana_status(elk_ip)
    logstash_status = check_logstash_status()
    openflow_status = check_openflow_status(onos_ip)

    return {
        "ELK": "UP" if elk_status else "DOWN",
        "ONOS": "UP" if onos_status else "DOWN",
        "KIBANA": "UP" if kibana_status else "DOWN",
        "LOGSTASH": "UP" if logstash_status else "DOWN",
        "OPENFLOW": "UP" if openflow_status else "DOWN",
    }
