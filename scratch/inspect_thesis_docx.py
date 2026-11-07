import zipfile
import xml.etree.ElementTree as ET

docx_path = r"D:\Project\Nhom02_SDNFlowGuard_Official_Submission\THESIS\BAO_CAO_DO_AN_CHUYEN_DE_SDNFLOWGUARD.docx"
with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read('word/document.xml')
    root = ET.fromstring(xml_content)
    paragraphs = []
    for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
        if texts:
            paragraphs.append("".join(texts))

print(f"Total paragraphs in Thesis: {len(paragraphs)}")

keywords = ["switch", "topo", "mininet", "icmp", "syn flood", "arp spoofing", "port scan", "4 switch", "bốn switch"]
for idx, p in enumerate(paragraphs):
    p_lower = p.lower()
    if any(k in p_lower for k in ["mô hình thực nghiệm", "kịch bản", "4 switch", "spine-leaf", "switch"]):
        if any(w in p_lower for w in ["topo", "kịch bản", "mininet", "switch"]):
            print(f"P{idx}: {p[:120]}...")
