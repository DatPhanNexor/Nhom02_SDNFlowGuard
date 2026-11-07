import json
import subprocess
import urllib.request
import psutil

def measure_resources():
    print("=" * 60)
    print("PHASE 4 RESOURCE & MEMORY AUDIT METRICS")
    print("=" * 60)

    # 1. Host Windows RAM
    vm = psutil.virtual_memory()
    total_gb = vm.total / (1024 ** 3)
    avail_gb = vm.available / (1024 ** 3)
    used_gb = vm.used / (1024 ** 3)
    print(f"Windows Host RAM: Total={total_gb:.2f} GB, Available={avail_gb:.2f} GB ({vm.available / vm.total * 100:.1f}%), Used={used_gb:.2f} GB ({vm.percent}%)")

    # 2. Docker inspect for all 6 containers
    containers = [
        "sdnflowguard-frontend",
        "sdnflowguard-backend",
        "sdnflowguard-onos",
        "sdnflowguard-elasticsearch",
        "sdnflowguard-logstash",
        "sdnflowguard-kibana",
    ]
    
    cmd = ["docker", "inspect"] + containers
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    inspect_data = json.loads(proc.stdout)

    print("\nContainer Inspection (OOMKilled, RestartCount, Memory Limits):")
    for item in inspect_data:
        name = item.get("Name", "").lstrip("/")
        state = item.get("State", {})
        host_cfg = item.get("HostConfig", {})
        status = state.get("Status")
        oom_killed = state.get("OOMKilled")
        restarts = item.get("RestartCount", 0)
        mem_limit_bytes = host_cfg.get("Memory", 0)
        mem_limit_mb = mem_limit_bytes / (1024 * 1024) if mem_limit_bytes else 0

        print(f"  [{name}] Status={status}, OOMKilled={oom_killed}, Restarts={restarts}, Limit={mem_limit_mb:.0f} MB")

    # 3. Docker stats live working sets
    print("\nLive Container Memory Usage (docker stats):")
    cmd_stats = ["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"]
    proc_stats = subprocess.run(cmd_stats, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    print(proc_stats.stdout.strip())

    # 4. Elasticsearch JVM Heap Pressure
    try:
        with urllib.request.urlopen("http://127.0.0.1:9200/_nodes/stats/jvm", timeout=5) as resp:
            es_jvm = json.loads(resp.read().decode("utf-8"))
            nodes = es_jvm.get("nodes", {})
            for node_id, node_info in nodes.items():
                jvm = node_info.get("jvm", {})
                mem = jvm.get("mem", {})
                heap_used = mem.get("heap_used_in_bytes", 0) / (1024 * 1024)
                heap_max = mem.get("heap_max_in_bytes", 0) / (1024 * 1024)
                heap_percent = mem.get("heap_used_percent", 0)
                print(f"\nElasticsearch JVM Heap: Used={heap_used:.1f} MB / Max={heap_max:.1f} MB ({heap_percent}%)")
    except Exception as e:
        print(f"Could not read ES JVM stats: {e}")

    # 5. Logstash JVM Heap Pressure
    try:
        with urllib.request.urlopen("http://127.0.0.1:5000/api/service-status", timeout=5) as resp:
            # We can check via logstash node stats directly if reachable from docker or service status
            pass
    except Exception as e:
        pass

    # 6. WSL2 available RAM
    try:
        wsl_proc = subprocess.run(["wsl", "-e", "free", "-m"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if wsl_proc.returncode == 0:
            print("\nWSL2 Ubuntu Memory (free -m):")
            print(wsl_proc.stdout.strip())
    except Exception as e:
        print(f"WSL2 measurement skipped: {e}")

if __name__ == "__main__":
    measure_resources()
