from PIL import Image

ico_path = r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\favicon.ico"
img = Image.open(ico_path)
print("Format:", img.format)
print("Size:", img.size)
print("info:", img.info)
# Check all sub-images in ICO
try:
    i = 0
    while True:
        img.seek(i)
        print(f"  Frame {i}: {img.size}, mode={img.mode}")
        i += 1
except EOFError:
    print(f"Total frames found: {i}")
