import os
import zipfile
import xml.etree.ElementTree as ET
from pypdf import PdfReader

out_dir = r"D:\Project\Nhom02_SDNFlowGuard\scratch\academic_extracted"
os.makedirs(out_dir, exist_ok=True)

# 1. Read DeTai.pdf
detai_pdf = r"C:\Users\Admin\Downloads\Course Materials-20261029T052523Z-1-001\Course Materials\DeTai.pdf"
if os.path.exists(detai_pdf):
    reader = PdfReader(detai_pdf)
    text = ""
    for idx, page in enumerate(reader.pages):
        text += f"\n--- PAGE {idx+1} ---\n" + page.extract_text()
    with open(os.path.join(out_dir, "DeTai.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"DeTai.pdf: {len(reader.pages)} pages extracted.")

# 2. Read QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf
quydinh_pdf = r"C:\Users\Admin\Downloads\Course Materials-20261029T052523Z-1-001\Course Materials\QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf"
if os.path.exists(quydinh_pdf):
    reader = PdfReader(quydinh_pdf)
    text = ""
    for idx, page in enumerate(reader.pages):
        text += f"\n--- PAGE {idx+1} ---\n" + page.extract_text()
    with open(os.path.join(out_dir, "QUY_DINH.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"QUY DINH.pdf: {len(reader.pages)} pages extracted.")

# 3. Read Yêu cầu đầu ra.pdf
yeucau_pdf = r"C:\Users\Admin\Downloads\Yêu cầu đầu ra.pdf"
if os.path.exists(yeucau_pdf):
    reader = PdfReader(yeucau_pdf)
    text = ""
    for idx, page in enumerate(reader.pages):
        text += f"\n--- PAGE {idx+1} ---\n" + page.extract_text()
    with open(os.path.join(out_dir, "Yeu_cau_dau_ra.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Yêu cầu đầu ra.pdf: {len(reader.pages)} pages extracted.")

# 4. Read Nhom02_PhanPhatDat_Tong_quan_de_tai.docx
docx_path = r"C:\Users\Admin\Downloads\Nhom02_PhanPhatDat_Tong_quan_de_tai.docx"
if os.path.exists(docx_path):
    with zipfile.ZipFile(docx_path, 'r') as z:
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        # Extract all text elements in order
        paragraphs = []
        for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [t.text for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if t.text]
            if texts:
                paragraphs.append("".join(texts))
        full_docx = "\n".join(paragraphs)
    with open(os.path.join(out_dir, "Tong_quan_de_tai.txt"), "w", encoding="utf-8") as f:
        f.write(full_docx)
    print(f"Tong_quan_de_tai.docx: {len(paragraphs)} paragraphs extracted.")

print("All extractions saved to:", out_dir)
