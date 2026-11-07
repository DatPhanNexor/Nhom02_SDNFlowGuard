from PIL import Image

img = Image.open(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png").convert("RGBA")
w, h = img.size

# Let's check where brightness is high (>200) vs deep blue (100-200) vs dark (<100)
# Create a small ASCII map (64x64)
small = img.resize((64, 64), Image.Resampling.LANCZOS)
ascii_chars = " .:-=+*#%@"
rows = []
for y in range(64):
    line = []
    for x in range(64):
        r, g, b, a = small.getpixel((x, y))
        if a < 50:
            line.append(" ")
        else:
            brightness = int(0.299*r + 0.587*g + 0.114*b)
            char_idx = int(brightness / 256 * len(ascii_chars))
            line.append(ascii_chars[min(char_idx, len(ascii_chars)-1)])
    rows.append("".join(line))

print("\n".join(rows))
