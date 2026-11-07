import os
import shutil
import hashlib

src_root = r"D:\Project\Nhom02_SDNFlowGuard"
sub_root = r"D:\Project\Nhom02_SDNFlowGuard_Official_Submission"
sub_source = os.path.join(sub_root, "SOURCE")

files_to_sync = [
    r"frontend\public\index.html",
    r"frontend\public\manifest.json",
    r"frontend\public\sdnflowguard-logo.svg",
    r"frontend\public\favicon.svg",
    r"frontend\public\favicon-32x32.png",
    r"frontend\public\favicon-16x16.png",
    r"frontend\public\favicon.ico",
    r"frontend\public\apple-touch-icon.png",
    r"frontend\public\logo192.png",
    r"frontend\public\logo512.png",
    r"frontend\public\sdnflowguard-logo.png",
    r"frontend\src\components\Header.js",
    r"frontend\src\components\Header.css",
    r"frontend\src\components\Sidebar.js",
    r"frontend\src\components\Sidebar.css",
]

print("=== 1. Syncing V5.2 Visual Identity Assets & Code ===")
for rel_path in files_to_sync:
    src_file = os.path.join(src_root, rel_path)
    dst_file = os.path.join(sub_source, rel_path)
    if os.path.exists(src_file):
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copy2(src_file, dst_file)
        print(f"  Synced: {rel_path}")
    else:
        print(f"  [MISSING in src]: {rel_path}")

print("\n=== 2. Syncing frontend/build ===")
src_build = os.path.join(src_root, "frontend", "build")
dst_build = os.path.join(sub_source, "frontend", "build")
if os.path.exists(src_build):
    if os.path.exists(dst_build):
        shutil.rmtree(dst_build)
    shutil.copytree(src_build, dst_build)
    print("  Copied frontend/build completely.")

print("\n=== 3. Regenerating CHECKSUM_SHA256.txt in Official Submission ===")
checksum_file = os.path.join(sub_root, "CHECKSUM_SHA256.txt")

entries = []
for root, dirs, files in os.walk(sub_source):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.pytest_cache', 'node_modules')]
    for file in files:
        if file.endswith(('.pyc', '.pyo')):
            continue
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, sub_root).replace('\\', '/')
        
        hasher = hashlib.sha256()
        with open(full_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        digest = hasher.hexdigest()
        entries.append(f"{digest}  {rel_path}\n")

entries.sort(key=lambda x: x.split('  ')[1])

with open(checksum_file, 'w', encoding='utf-8') as f:
    f.writelines(entries)

print(f"Wrote {len(entries)} file checksums to {checksum_file}")

# Verify checksums
mismatches = 0
with open(checksum_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        expected_hash, rel_path = line.split('  ', 1)
        full_path = os.path.join(sub_root, rel_path.replace('/', '\\'))
        if not os.path.exists(full_path):
            print(f"Missing file: {rel_path}")
            mismatches += 1
            continue
        hasher = hashlib.sha256()
        with open(full_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        if hasher.hexdigest() != expected_hash:
            print(f"Hash mismatch: {rel_path}")
            mismatches += 1

print(f"Checksum verification complete: {len(entries)} verified, {mismatches} mismatches.")
