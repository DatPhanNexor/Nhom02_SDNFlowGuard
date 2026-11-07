import os
import zipfile

# Check python libraries available
try:
    import pypdf
    has_pypdf = True
except ImportError:
    has_pypdf = False

try:
    import docx
    has_docx = True
except ImportError:
    has_docx = False

print(f"has_pypdf: {has_pypdf}, has_docx: {has_docx}")

# Inspect zips
cm_zip = r"C:\Users\Admin\Downloads\Course Materials-20261029T052523Z-1-001\Course Materials\Course Materials.zip"
if os.path.exists(cm_zip):
    with zipfile.ZipFile(cm_zip, 'r') as z:
        print("\nCourse Materials.zip contains:")
        for name in z.namelist()[:20]:
            print("  ", name)
        if len(z.namelist()) > 20:
            print(f"  ... and {len(z.namelist()) - 20} more files")

ceh_zip = r"C:\Users\Admin\Downloads\CEH v13 PDF.zip"
if os.path.exists(ceh_zip):
    with zipfile.ZipFile(ceh_zip, 'r') as z:
        print("\nCEH v13 PDF.zip contains:")
        for name in z.namelist()[:20]:
            print("  ", name)
        if len(z.namelist()) > 20:
            print(f"  ... and {len(z.namelist()) - 20} more files")
