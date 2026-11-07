import os

target_names = [
    "Course Materials.zip",
    "CEH v13 PDF.zip",
    "DeTai.pdf",
    "QUY DINH TRINH BAY BAO CAO BAI TẬP LỚN.pdf",
    "Yêu cầu đầu ra.pdf",
    "Nhom02_PhanPhatDat_Tong_quan_de_tai.docx",
]

search_roots = [
    r"D:\Project\Nhom02_SDNFlowGuard",
    r"D:\Project\Nhom02_SDNFlowGuard_Official_Submission",
    r"C:\Users\Admin\Downloads",
    r"C:\Users\Admin\Desktop",
    r"C:\Users\Admin\Documents",
    "D:\\",
]

found_map = {name: [] for name in target_names}

for sroot in search_roots:
    if not os.path.exists(sroot):
        continue
    print(f"Scanning: {sroot} ...")
    # Don't recurse indefinitely into massive directories if under D:\
    max_depth = 4 if sroot == "D:\\" else 8
    base_depth = sroot.count(os.sep)
    for root, dirs, files in os.walk(sroot):
        # Prune node_modules, .git, venv
        dirs[:] = [d for d in dirs if d not in ('node_modules', '.git', 'venv', '.gradle', 'build', 'intermediates')]
        cur_depth = root.count(os.sep) - base_depth
        if cur_depth > max_depth:
            dirs[:] = []
            continue
        for f in files:
            for tname in target_names:
                if f.lower() == tname.lower():
                    found_map[tname].append(os.path.join(root, f))

print("\n" + "=" * 60)
print("ACADEMIC DOCUMENT SEARCH RESULTS:")
print("=" * 60)
for tname in target_names:
    matches = found_map[tname]
    if matches:
        print(f"[FOUND] {tname}:")
        for m in matches:
            print(f"   -> {m} ({os.path.getsize(m)} bytes)")
    else:
        print(f"[NOT FOUND] {tname}")
