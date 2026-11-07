import asyncio
import json
import os
import subprocess
import urllib.request
import aiohttp

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9223
USER_DATA_DIR = r"D:\Project\Nhom02_SDNFlowGuard\scratch\chrome_profile_logo"
OUT_IMG = r"C:\Users\Admin\.gemini\antigravity\brain\f55b3611-32fe-47cd-9251-7af52f3afbcf\sdnflowguard_dashboard_logo_verified.png"

async def test_logo():
    # 1. Start Chrome headless
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1440,900"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Launched headless Chrome...")
    await asyncio.sleep(2)

    try:
        # Get websocket URL
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

                # Navigate to Dashboard
                print("Navigating to http://127.0.0.1:3000/ ...")
                await send("Page.navigate", {"url": "http://127.0.0.1:3000/"})
                await asyncio.sleep(4)

                # Check computed styles of logo in Header and Sidebar
                js_eval = """
                (() => {
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
                            fontSize: style.fontSize,
                            fontWeight: style.fontWeight,
                            text: el.innerText || null
                        };
                    };

                    return {
                        headerLogo: getInfo(hLogo),
                        headerText: getInfo(hText),
                        sidebarLogo: getInfo(sLogo),
                        sidebarText: getInfo(sText)
                    };
                })()
                """
                eval_res = await send("Runtime.evaluate", {"expression": js_eval, "returnByValue": True})
                info = eval_res.get("result", {}).get("value", {})
                print("\n=== LOGO & BRAND MEASUREMENTS ===")
                print(json.dumps(info, indent=2, ensure_ascii=False))

                # Capture screenshot
                shot = await send("Page.captureScreenshot", {"format": "png"})
                import base64
                img_data = base64.b64decode(shot["data"])
                with open(OUT_IMG, "wb") as f:
                    f.write(img_data)
                print(f"\nSaved screenshot to: {OUT_IMG} ({len(img_data)} bytes)")

    finally:
        proc.terminate()
        proc.wait()
        print("Chrome closed.")

if __name__ == "__main__":
    asyncio.run(test_logo())
