from PIL import Image

img = Image.open(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png").convert("RGBA")

# Let's inspect the colors across a horizontal line through the center (y=256)
print("Colors across horizontal center line (y=256):")
for x in range(60, 480, 20):
    p = img.getpixel((x, 256))
    if p[3] > 50:
        print(f"  x={x:3d}: RGBA={p} -> hex=#{p[0]:02x}{p[1]:02x}{p[2]:02x}")

print("\nColors across vertical center line (x=268):")
for y in range(60, 480, 20):
    p = img.getpixel((268, y))
    if p[3] > 50:
        print(f"  y={y:3d}: RGBA={p} -> hex=#{p[0]:02x}{p[1]:02x}{p[2]:02x}")
