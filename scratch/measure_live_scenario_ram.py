import time
import subprocess
import urllib.request
import base64
import json
import psutil

onos_auth = "Basic " + base64.b64encode(b"onos:rocks").decode("ascii")

def run_traffic_burst(count=10):
    for i in range(count):
        # Frontend
        try:
            urllib.request.urlopen("http://127.0.0.1:3000/", timeout=3)
        except Exception:
            pass
        # Backend health & stats
        try:
            urllib.request.urlopen("http://127.0.0.1:5000/api/health", timeout=3)
            urllib.request.urlopen("http://127.0.0.1:5000/api/service-status", timeout=3)
            urllib.request.urlopen("http://127.0.0.1:5000/api/logstash/pipeline-status", timeout=3)
            urllib.request.urlopen("http://127.0.0.1:5000/api/topology", timeout=3)
        except Exception:
            pass
        # Elasticsearch
        try:
            urllib.request.urlopen("http://127.0.0.1:9200/", timeout=3)
        except Exception:
            pass
        # Kibana
        try:
            urllib.request.urlopen("http://127.0.0.1:5601/api/status", timeout=3)
        except Exception:
            pass
        # ONOS
        try:
            req_d = urllib.request.Request("http://127.0.0.1:8181/onos/v1/devices", headers={"Authorization": onos_auth})
            urllib.request.urlopen(req_d, timeout=3)
            req_f = urllib.request.Request("http://127.0.0.1:8181/onos/v1/flows", headers={"Authorization": onos_auth})
            urllib.request.urlopen(req_f, timeout=3)
        except Exception:
            pass
        # Logstash probe & POST
        try:
            urllib.request.urlopen("http://127.0.0.1:18080/", timeout=3)
            req_post = urllib.request.Request(
                "http://127.0.0.1:18080/",
                data=b'{"type":"burst_test","timestamp":' + str(time.time()).encode() + b'}',
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req_post, timeout=3)
        except Exception:
            pass
        time.sleep(0.1)

print("=== RUNNING LIVE DEMO WORKLOAD & MEASURING RAM ===")
print("Executing 15 concurrent load cycles across all 6 services...")
t0 = time.time()
run_traffic_burst(15)
elapsed = time.time() - t0
print(f"Workload completed in {elapsed:.2f}s.")

# Host RAM
vm = psutil.virtual_memory()
print(f"\nHost Windows RAM under load:")
print(f"  Total: {vm.total / (1024**3):.2f} GB")
print(f"  Available: {vm.available / (1024**3):.2f} GB ({vm.available / vm.total * 100:.1f}%)")
print(f"  Used: {vm.used / (1024**3):.2f} GB ({vm.percent}%)")

# Docker stats
cmd_stats = ["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.CPUPerc}}"]
proc_stats = subprocess.run(cmd_stats, stdout=subprocess.PIPE, text=True, check=True)
print("\nContainer Working Sets under active load:")
print(proc_stats.stdout.strip())

# Inspect containers
containers = ["sdnflowguard-frontend", "sdnflowguard-backend", "sdnflowguard-onos", "sdnflowguard-elasticsearch", "sdnflowguard-logstash", "sdnflowguard-kibana"]
proc_inspect = subprocess.run(["docker", "inspect"] + containers, stdout=subprocess.PIPE, text=True, check=True)
inspect_data = json.loads(proc_inspect.stdout)
print("\nContainer Health & Lifecycle:")
for c in inspect_data:
    name = c.get("Name", "").lstrip("/")
    state = c.get("State", {})
    print(f"  {name}: status={state.get('Status')}, oom_killed={state.get('OOMKilled')}, restarts={c.get('RestartCount')}")
