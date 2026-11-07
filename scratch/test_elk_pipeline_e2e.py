import json
import time
import urllib.request
import uuid

def test_pipeline():
    test_id = f"audit_v50_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    print(f"Generated Unique Test ID: {test_id}")

    # 1. Test Logstash HTTP probe (GET)
    req_probe = urllib.request.Request("http://127.0.0.1:18080/", method="GET")
    with urllib.request.urlopen(req_probe, timeout=5) as resp:
        probe_body = resp.read().decode("utf-8")
        print(f"1. Logstash HTTP Probe (GET /): status={resp.status}, body={probe_body.strip()}")
        assert resp.status == 200
        assert probe_body.strip() == "ok"

    # 2. Ingest test event via POST
    payload = {
        "audit_id": test_id,
        "type": "sdn_audit_telemetry",
        "source": "v50_persistence_audit",
        "description": "SDNFlowGuard V5.0 End-to-End Ingestion Audit Event",
        "timestamp": time.time(),
    }
    data = json.dumps(payload).encode("utf-8")
    req_post = urllib.request.Request(
        "http://127.0.0.1:18080/",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_post, timeout=5) as resp:
        post_body = resp.read().decode("utf-8")
        print(f"2. Logstash Ingest Event (POST /): status={resp.status}, body={post_body.strip()}")
        assert resp.status == 200
        assert post_body.strip() == "ok"

    # Wait for Logstash batch flush to Elasticsearch (batch size 50 or default flush interval)
    print("Waiting 3 seconds for Logstash pipeline to filter and index event into Elasticsearch...")
    time.sleep(3)

    # 3. Check Backend Pipeline Stats API
    req_stats = urllib.request.Request("http://127.0.0.1:5000/api/logstash/pipeline-status", method="GET")
    with urllib.request.urlopen(req_stats, timeout=5) as resp:
        stats_body = json.loads(resp.read().decode("utf-8"))
        print(f"3. Backend Pipeline Stats (/api/logstash/pipeline-status): status={resp.status}")
        data_stats = stats_body.get("data", {})
        print(f"   Pipeline ID: {data_stats.get('pipeline_id')}")
        print(f"   Status: {data_stats.get('status')}")
        print(f"   Events Received: {data_stats.get('events_received')}")
        print(f"   Events Filtered: {data_stats.get('events_filtered')}")
        print(f"   Events Emitted: {data_stats.get('events_emitted')}")
        print(f"   Documents Indexed: {data_stats.get('documents_indexed')}")
        print(f"   Queue Backpressure: {data_stats.get('queue_backpressure')}")

    # 4. Query Elasticsearch directly for the unique test_id
    es_query_url = f"http://127.0.0.1:9200/sdnflowguard-events-*/_search?q=audit_id:{test_id}"
    req_es = urllib.request.Request(es_query_url, method="GET")
    with urllib.request.urlopen(req_es, timeout=5) as resp:
        es_data = json.loads(resp.read().decode("utf-8"))
        hits = es_data.get("hits", {}).get("hits", [])
        total_hits = es_data.get("hits", {}).get("total", {}).get("value", 0)
        print(f"4. Elasticsearch Search (q=audit_id:{test_id}): total_hits={total_hits}")
        if total_hits > 0:
            doc = hits[0]
            print(f"   [SUCCESS] Document ID: {doc.get('_id')}")
            print(f"   Index: {doc.get('_index')}")
            print(f"   Source: {json.dumps(doc.get('_source'), indent=2)}")
            print(">>> PIPELINE END-TO-END VERIFICATION: PASS <<<")
            return True
        else:
            print(">>> PIPELINE END-TO-END VERIFICATION: FAIL (Document not indexed yet) <<<")
            return False

if __name__ == "__main__":
    success = test_pipeline()
    exit(0 if success else 1)
