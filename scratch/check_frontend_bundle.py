import re
import urllib.request

def check_frontend():
    with urllib.request.urlopen("http://127.0.0.1:3000/", timeout=5) as resp:
        html = resp.read().decode("utf-8")
        match = re.search(r'static/js/main\.[a-f0-9]+\.js', html)
        if not match:
            print("ERROR: main.js not found in HTML")
            return False
        js_path = match.group(0)
        print(f"Discovered JS bundle: {js_path}")

    with urllib.request.urlopen(f"http://127.0.0.1:3000/{js_path}", timeout=5) as resp:
        js = resp.read().decode("utf-8")
        has_logstash = "api/logstash/pipeline-status" in js
        has_card = "Logstash Pipeline" in js or "Trạng thái Pipeline" in js or "documents_indexed" in js
        print(f"Contains 'api/logstash/pipeline-status': {has_logstash}")
        print(f"Contains Logstash Pipeline UI terms: {has_card}")
        return has_logstash and has_card

if __name__ == "__main__":
    ok = check_frontend()
    print("FRONTEND BUNDLE IN NEW CONTAINER VERIFIED:" if ok else "FRONTEND CHECK FAILED", ok)
    exit(0 if ok else 1)
