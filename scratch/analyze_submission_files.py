import os
from collections import Counter

sub_root = r"D:\Project\Nhom02_SDNFlowGuard_Official_Submission\SOURCE"

counts = Counter()
ext_counts = Counter()
dir_counts = Counter()

for root, dirs, files in os.walk(sub_root):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.pytest_cache', 'node_modules')]
    for f in files:
        if f.endswith(('.pyc', '.pyo')):
            continue
        full = os.path.join(root, f)
        rel = os.path.relpath(full, sub_root)
        top_dir = rel.split(os.sep)[0]
        ext = os.path.splitext(f)[1].lower() or "no_ext"
        
        counts['total'] += 1
        dir_counts[top_dir] += 1
        ext_counts[ext] += 1

print(f"Total files in SOURCE: {counts['total']}")
print("\nBreakdown by top-level directory:")
for d, c in dir_counts.most_common():
    print(f"  {d:25s}: {c:5d} files ({c/counts['total']*100:.1f}%)")

print("\nBreakdown by file extension (Top 15):")
for ext, c in ext_counts.most_common(15):
    print(f"  {ext:10s}: {c:5d} files")
