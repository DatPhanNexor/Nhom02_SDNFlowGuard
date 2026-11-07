import json
import base64
import urllib.request

auth_header = "Basic " + base64.b64encode(b"onos:rocks").decode("ascii")

def query_onos(endpoint):
    url = f"http://127.0.0.1:8181/onos/v1{endpoint}"
    req = urllib.request.Request(url, headers={"Authorization": auth_header})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

print("=== ONOS TOPOLOGY AUDIT ===")
devices = query_onos("/devices").get("devices", [])
print(f"1. Devices Count: {len(devices)}")
for d in devices:
    print(f"   ID: {d.get('id')}, Available: {d.get('available')}, Role: {d.get('role')}, HW: {d.get('hw')}, SW: {d.get('sw')}, Driver: {d.get('driver')}, Protocol: {d.get('annotations', {}).get('protocol')}")

hosts = query_onos("/hosts").get("hosts", [])
print(f"\n2. Hosts Count: {len(hosts)}")
for h in hosts:
    print(f"   ID: {h.get('id')}, IP: {h.get('ipAddresses')}, MAC: {h.get('mac')}, Locations: {h.get('locations')}")

flows = query_onos("/flows").get("flows", [])
print(f"\n3. Flows Count: {len(flows)}")
for f in flows:
    print(f"   Flow ID: {f.get('id')}, Device: {f.get('deviceId')}, State: {f.get('state')}, Table: {f.get('tableId')}, Priority: {f.get('priority')}, Packets: {f.get('packets')}, Bytes: {f.get('bytes')}")

ports = query_onos("/statistics/ports").get("statistics", [])
print(f"\n4. Port Statistics Device Entries: {len(ports)}")
for p in ports:
    device_id = p.get("device")
    p_stats = p.get("ports", [])
    print(f"   Device: {device_id}, Active Ports with stats: {len(p_stats)}")
    for port_info in p_stats:
        print(f"      Port {port_info.get('port')}: pktRx={port_info.get('packetsReceived')}, pktTx={port_info.get('packetsSent')}, bytesRx={port_info.get('bytesReceived')}, bytesTx={port_info.get('bytesSent')}")

links = query_onos("/links").get("links", [])
print(f"\n5. Links Count: {len(links)}")
for l in links:
    print(f"   Link: {l.get('src')} -> {l.get('dst')}, State: {l.get('state')}")
