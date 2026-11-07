import os
from PIL import Image

pub_dir = r"D:\Project\Nhom02_SDNFlowGuard\frontend\public"
assets = [
    "favicon.ico",
    "apple-touch-icon.png",
    "logo192.png",
    "logo512.png",
    "sdnflowguard-logo.png"
]

print("=== IMAGE ASSET INSPECTION ===")
for a in assets:
    p = os.path.join(pub_dir, a)
    if not os.path.exists(p):
        print(f"File not found: {a}")
        continue
    size_bytes = os.path.getsize(p)
    try:
        img = Image.open(p)
        print(f"\n{a}:")
        print(f"  Format: {img.format}, Size: {img.size}, Mode: {img.mode}, Bytes: {size_bytes}")
        if a == "favicon.ico":
            # Check frames in ICO
            frames = []
            try:
                for i in range(10):
                    img.seek(i)
                    frames.append(img.size)
            except EOFError:
                pass
            print(f"  ICO sizes/frames: {frames}")
    except Exception as e:
        print(f"Error inspecting {a}: {e}")
