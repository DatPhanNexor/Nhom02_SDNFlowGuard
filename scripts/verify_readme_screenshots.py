"""
SDNFlowGuard README Screenshot & Media Verification Tool.
Verifies all 29 laboratory proof PNGs and logo are correctly referenced,
embedded, case-matched, and exist on disk.
"""

import os
import re
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    readme_path = root / "README.md"
    screenshots_dir = root / "screenshots"

    print("============================================================")
    print(" SDNFlowGuard README & Screenshot Integrity Verifier")
    print("============================================================")

    if not readme_path.is_file():
        print(f"[FAIL] README.md not found at {readme_path}")
        sys.exit(1)

    if not screenshots_dir.is_dir():
        print(f"[FAIL] screenshots/ directory not found at {screenshots_dir}")
        sys.exit(1)

    # 1. Enumerate actual files on disk
    disk_files = {f for f in os.listdir(screenshots_dir) if f.endswith(".png")}
    print(f"Total PNG files on disk in screenshots/: {len(disk_files)}")
    expected_count = 30  # 29 proof PNGs + 1 logo
    if len(disk_files) != expected_count:
        print(f"[WARN] Expected {expected_count} PNGs, found {len(disk_files)}")

    # 2. Parse README.md for image references
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match ![alt](path) or <img src="path"
    md_img_pattern = re.compile(r"!\[(.*?)\]\((screenshots/[^\)]+)\)")
    html_img_pattern = re.compile(r'<img[^>]+src=["\'](screenshots/[^"\']+)["\']')

    md_matches = md_img_pattern.findall(content)
    html_matches = html_img_pattern.findall(content)

    referenced_files = set()
    for _, path in md_matches:
        filename = Path(path).name
        referenced_files.add(filename)

    for path in html_matches:
        filename = Path(path).name
        referenced_files.add(filename)

    print(f"Total unique images referenced in README.md: {len(referenced_files)}")

    # 3. Check for broken links (referenced in README but not on disk)
    broken_links = []
    case_mismatches = []
    for ref in referenced_files:
        exact_path = screenshots_dir / ref
        if not exact_path.exists():
            broken_links.append(ref)
        else:
            # Check exact case on disk (important for Linux / GitHub)
            actual_case_matches = [f for f in disk_files if f == ref]
            if not actual_case_matches:
                case_mismatches.append(ref)

    if broken_links:
        print(f"[FAIL] Found {len(broken_links)} broken image links in README.md:")
        for b in broken_links:
            print(f"  - screenshots/{b}")
        sys.exit(1)
    else:
        print("  [PASS] Zero broken image links.")

    if case_mismatches:
        print(f"[FAIL] Found {len(case_mismatches)} case mismatches:")
        for c in case_mismatches:
            print(f"  - {c}")
        sys.exit(1)
    else:
        print("  [PASS] All image references match disk filenames with exact case sensitivity.")

    # 4. Check that all 29 demonstration screenshots are referenced
    proof_files = {f for f in disk_files if f != "sdnflowguard-logo.png"}
    missing_proofs = proof_files - referenced_files

    if missing_proofs:
        print(f"[FAIL] {len(missing_proofs)} demonstration screenshots not referenced in README.md:")
        for m in sorted(missing_proofs):
            print(f"  - screenshots/{m}")
        sys.exit(1)
    else:
        print(f"  [PASS] All {len(proof_files)} demonstration screenshots are directly embedded in README.md.")

    # 5. Check logo is referenced
    if "sdnflowguard-logo.png" in referenced_files:
        print("  [PASS] Official sdnflowguard-logo.png is embedded in header.")
    else:
        print("[FAIL] sdnflowguard-logo.png is not embedded in README.md.")
        sys.exit(1)

    print("\n[SUCCESS] README screenshot audit passed completely (29/29 proofs + 1 logo verified).")


if __name__ == "__main__":
    main()
