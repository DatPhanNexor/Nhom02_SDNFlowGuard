import urllib.request

endpoints = [
    ("/favicon.svg", "image/svg+xml"),
    ("/favicon-32x32.png", "image/png"),
    ("/favicon-16x16.png", "image/png"),
    ("/favicon.ico", "image/x-icon"),
    ("/apple-touch-icon.png", "image/png"),
    ("/sdnflowguard-logo.svg", "image/svg+xml"),
    ("/manifest.json", "application/json"),
]

print("=== VERIFYING ASSET HTTP STATUS & CONTENT-TYPES ===")
all_pass = True
for ep, expected_mime in endpoints:
    url = f"http://127.0.0.1:3000{ep}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=4) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            length = len(resp.read())
            mime_match = expected_mime in content_type or (ep.endswith(".ico") and "icon" in content_type)
            ok = (status == 200) and mime_match
            print(f"[{'PASS' if ok else 'FAIL'}] {ep:25s}: Status={status}, Content-Type={content_type}, Length={length} bytes")
            if not ok:
                all_pass = False
    except Exception as e:
        print(f"[FAIL] {ep:25s}: Exception: {e}")
        all_pass = False

print("\nAsset Endpoints Verdict:", "ALL PASS" if all_pass else "SOME FAILED")
