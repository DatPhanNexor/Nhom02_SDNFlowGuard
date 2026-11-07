from PIL import Image
from collections import Counter

img = Image.open(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png").convert("RGBA")
pixels = list(img.getdata())
colors = Counter([p for p in pixels if p[3] > 50])

print("Top 15 opaque/semi-opaque colors in logo:")
for c, cnt in colors.most_common(15):
    print(f"  RGBA{c}: count={cnt} ({cnt/len(pixels)*100:.2f}%) - hex: #{c[0]:02x}{c[1]:02x}{c[2]:02x}")
