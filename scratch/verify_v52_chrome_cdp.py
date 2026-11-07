import asyncio
import json
import os
import subprocess
import aiohttp
import base64

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9225
USER_DATA_DIR = r"D:\Project\Nhom02_SDNFlowGuard\scratch\chrome_profile_v52"
ARTIFACT_DIR = r"C:\Users\Admin\.gemini\antigravity\brain\f55b3611-32fe-47cd-9251-7af52f3afbcf"

async def test_chrome():
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1920,1080"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Launched Chrome CDP...")
    await asyncio.sleep(2)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{CDP_PORT}/json") as resp:
                tabs = await resp.json()
                ws_url = tabs[0]["webSocketDebuggerUrl"]

        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(ws_url) as ws:
                msg_id = 1
                async def send(method, params=None):
                    nonlocal msg_id
                    mid = msg_id
                    msg_id += 1
                    payload = {"id": mid, "method": method, "params": params or {}}
                    await ws.send_json(payload)
                    while True:
                        res = await ws.receive_json()
                        if res.get("id") == mid:
                            return res.get("result", {})

                await send("Page.enable")
                await send("Runtime.enable")

                console_errors = []
                async def listen():
                    while True:
                        try:
                            msg = await ws.receive_json()
                            if msg.get("method") == "Runtime.consoleAPICalled":
                                if msg.get("params", {}).get("type") == "error":
                                    console_errors.append(msg)
                        except Exception:
                            break

                asyncio.create_task(listen())

                # Navigate at 1920x1080
                print("1. Testing 1920x1080 viewport...")
                await send("Emulation.setDeviceMetricsOverride", {
                    "width": 1920,
                    "height": 1080,
                    "deviceScaleFactor": 1,
                    "mobile": False
                })
                await send("Page.navigate", {"url": "http://127.0.0.1:3000/"})
                await asyncio.sleep(4)

                js_audit = """
                (() => {
                    const favicons = Array.from(document.querySelectorAll('link[rel*="icon"]')).map(l => ({
                        rel: l.rel,
                        type: l.type,
                        href: l.href,
                        sizes: l.sizes ? l.sizes.value : null
                    }));

                    const hLogo = document.querySelector('.header-brand-logo');
                    const hText = document.querySelector('.header-brand-text, .header h1');
                    const sLogo = document.querySelector('.sidebar-brand-logo');
                    const sText = document.querySelector('.sidebar-brand-text, .sidebar-title span');

                    const getInfo = (el) => {
                        if (!el) return null;
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return {
                            tag: el.tagName,
                            width: rect.width,
                            height: rect.height,
                            src: el.src || null,
                            naturalWidth: el.naturalWidth || null,
                            naturalHeight: el.naturalHeight || null,
                            imageRendering: style.imageRendering,
                            filter: style.filter,
                            fontSize: style.fontSize,
                            fontWeight: style.fontWeight
                        };
                    };

                    const noOverflow = document.documentElement.scrollWidth <= window.innerWidth;

                    return {
                        favicons: favicons,
                        headerLogo: getInfo(hLogo),
                        headerText: getInfo(hText),
                        sidebarLogo: getInfo(sLogo),
                        sidebarText: getInfo(sText),
                        noHorizontalOverflow: noOverflow,
                        scrollWidth: document.documentElement.scrollWidth,
                        innerWidth: window.innerWidth
                    };
                })()
                """
                eval_res = await send("Runtime.evaluate", {"expression": js_audit, "returnByValue": True})
                audit_1920 = eval_res.get("result", {}).get("value", {})
                print("\n=== 1920x1080 AUDIT METRICS ===")
                print(json.dumps(audit_1920, indent=2, ensure_ascii=False))

                # Screenshot at 1920x1080
                shot1 = await send("Page.captureScreenshot", {"format": "png"})
                img1_path = os.path.join(ARTIFACT_DIR, "sdnflowguard_v52_full_desktop_1920.png")
                with open(img1_path, "wb") as f:
                    f.write(base64.b64decode(shot1["data"]))
                print(f"Saved 1920x1080 screenshot: {img1_path}")

                # 2. Testing 1366x768 viewport (Laptop)
                print("\n2. Testing 1366x768 laptop viewport...")
                await send("Emulation.setDeviceMetricsOverride", {
                    "width": 1366,
                    "height": 768,
                    "deviceScaleFactor": 1,
                    "mobile": False
                })
                await asyncio.sleep(2)

                eval_1366 = await send("Runtime.evaluate", {"expression": js_audit, "returnByValue": True})
                audit_1366 = eval_1366.get("result", {}).get("value", {})
                print("1366x768 noHorizontalOverflow:", audit_1366.get("noHorizontalOverflow"))

                shot2 = await send("Page.captureScreenshot", {"format": "png"})
                img2_path = os.path.join(ARTIFACT_DIR, "sdnflowguard_v52_laptop_1366.png")
                with open(img2_path, "wb") as f:
                    f.write(base64.b64decode(shot2["data"]))
                print(f"Saved 1366x768 screenshot: {img2_path}")

                print(f"\nConsole Errors Count: {len(console_errors)}")

    finally:
        proc.terminate()
        proc.wait()
        print("Chrome CDP completed.")

if __name__ == "__main__":
    asyncio.run(test_chrome())
