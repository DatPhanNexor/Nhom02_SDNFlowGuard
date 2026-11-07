from PIL import Image

img = Image.open(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png").convert("RGBA")
w, h = img.size

# Sample lines across the image
print(f"Image size: {w}x{h}")

# Check colors in the center (w//2, h//2)
for y in range(50, 480, 50):
    row_pixels = [img.getpixel((x, y)) for x in range(50, 480, 50)]
    opaque = [p for p in row_pixels if p[3] > 100]
    print(f"y={y}: opaque count={len(opaque)}/9, sample center pixel={img.getpixel((w//2, y))}")
