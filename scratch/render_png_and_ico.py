import os
import asyncio
import subprocess
import base64
import aiohttp
from PIL import Image

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CDP_PORT = 9224
USER_DATA_DIR = r"D:\Project\Nhom02_SDNFlowGuard\scratch\chrome_profile_render"
PUB_DIR = r"D:\Project\Nhom02_SDNFlowGuard\frontend\public"

SVG_LOGO_PATH = os.path.join(PUB_DIR, "sdnflowguard-logo.svg").replace('\\', '/')
SVG_FAVICON_PATH = os.path.join(PUB_DIR, "favicon.svg").replace('\\', '/')

async def render_svg(svg_path, size):
    # Create temporary HTML to display SVG at exact size
    html = f"""<!DOCTYPE html>
<html>
<head>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: transparent; overflow: hidden; width: {size}px; height: {size}px; }}
    img {{ width: {size}px; height: {size}px; display: block; }}
  </style>
</head>
<body>
  <img src="file:///{svg_path}" width="{size}" height="{size}" />
</body>
</html>"""
    tmp_html = os.path.join(r"D:\Project\Nhom02_SDNFlowGuard\scratch", f"render_{size}.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html)
    return tmp_html

async def main():
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={CDP_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--window-size=1000,1000"
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Launched headless Chrome for SVG rendering...")
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
                await send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})

                async def capture(svg_file, size, out_png):
                    html_file = await render_svg(svg_file, size)
                    file_url = f"file:///{html_file.replace(os.sep, '/')}"
                    await send("Emulation.setDeviceMetricsOverride", {
                        "width": size,
                        "height": size,
                        "deviceScaleFactor": 1,
                        "mobile": False
                    })
                    await send("Page.navigate", {"url": file_url})
                    await asyncio.sleep(0.5)
                    shot = await send("Page.captureScreenshot", {"format": "png", "fromSurface": True})
                    data = base64.b64decode(shot["data"])
                    with open(out_png, "wb") as f:
                        f.write(data)
                    print(f"Rendered {size}x{size} PNG: {out_png}")

                # Render favicon sizes using optical-sized favicon.svg
                fav_16 = os.path.join(PUB_DIR, "favicon-16x16.png")
                fav_32 = os.path.join(PUB_DIR, "favicon-32x32.png")
                fav_48 = os.path.join(r"D:\Project\Nhom02_SDNFlowGuard\scratch", "fav_48.png")
                fav_64 = os.path.join(r"D:\Project\Nhom02_SDNFlowGuard\scratch", "fav_64.png")
                fav_128 = os.path.join(r"D:\Project\Nhom02_SDNFlowGuard\scratch", "fav_128.png")
                fav_256 = os.path.join(r"D:\Project\Nhom02_SDNFlowGuard\scratch", "fav_256.png")

                await capture(SVG_FAVICON_PATH, 16, fav_16)
                await capture(SVG_FAVICON_PATH, 32, fav_32)
                await capture(SVG_FAVICON_PATH, 48, fav_48)
                await capture(SVG_FAVICON_PATH, 64, fav_64)
                await capture(SVG_FAVICON_PATH, 128, fav_128)
                await capture(SVG_FAVICON_PATH, 256, fav_256)

                # Render brand logo sizes using sdnflowguard-logo.svg
                apple_icon = os.path.join(PUB_DIR, "apple-touch-icon.png")
                logo192 = os.path.join(PUB_DIR, "logo192.png")
                logo512 = os.path.join(PUB_DIR, "logo512.png")
                sdn_png = os.path.join(PUB_DIR, "sdnflowguard-logo.png")

                await capture(SVG_LOGO_PATH, 180, apple_icon)
                await capture(SVG_LOGO_PATH, 192, logo192)
                await capture(SVG_LOGO_PATH, 512, logo512)
                await capture(SVG_LOGO_PATH, 512, sdn_png)

                # Now assemble multi-frame favicon.ico with PIL
                img_16 = Image.open(fav_16).convert("RGBA")
                img_32 = Image.open(fav_32).convert("RGBA")
                img_48 = Image.open(fav_48).convert("RGBA")
                img_64 = Image.open(fav_64).convert("RGBA")
                img_128 = Image.open(fav_128).convert("RGBA")
                img_256 = Image.open(fav_256).convert("RGBA")

                ico_path = os.path.join(PUB_DIR, "favicon.ico")
                img_256.save(
                    ico_path,
                    format="ICO",
                    sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
                    append_images=[img_128, img_64, img_48, img_32, img_16]
                )
                print(f"Generated multi-frame favicon.ico at: {ico_path}")

    finally:
        proc.terminate()
        proc.wait()
        print("Done rendering assets.")

if __name__ == "__main__":
    asyncio.run(main())
