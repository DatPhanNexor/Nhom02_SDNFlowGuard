from PIL import Image

def analyze_alpha_bbox(path):
    img = Image.open(path)
    bbox = img.getbbox()
    w, h = img.size
    print(f"\nAnalysis of {path}:")
    print(f"  Canvas size: {w}x{h}")
    print(f"  Non-transparent bounding box: {bbox}")
    if bbox:
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        print(f"  Shield content width: {bw} ({bw/w*100:.1f}%), height: {bh} ({bh/h*100:.1f}%)")
        print(f"  Padding: left={bbox[0]}, top={bbox[1]}, right={w-bbox[2]}, bottom={h-bbox[3]}")

analyze_alpha_bbox(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\sdnflowguard-logo.png")
analyze_alpha_bbox(r"D:\Project\Nhom02_SDNFlowGuard\frontend\public\favicon.ico")
