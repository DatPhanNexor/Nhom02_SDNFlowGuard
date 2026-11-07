import pathlib
import subprocess

readme_path = pathlib.Path('d:/Project/Nhom02_SDNFlowGuard/README.md')
readme_text = readme_path.read_text(encoding='utf-8')
logo_uri = pathlib.Path('d:/Project/Nhom02_SDNFlowGuard/screenshots/sdnflowguard-logo.png').resolve().as_uri()

# Escape for JS string template
js_readme = readme_text.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
js_logo = logo_uri.replace('\\', '\\\\')

html_template = """<!DOCTYPE html>
<html lang="vi" data-color-mode="dark" data-dark-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SDNFlowGuard README Preview</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  body {
    background-color: #0d1117;
    margin: 0;
    padding: 30px;
    display: flex;
    justify-content: center;
  }
  .markdown-body {
    box-sizing: border-box;
    width: 100%;
    max-width: 980px;
    margin: 0 auto;
    padding: 45px;
    background-color: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;
  }
  .markdown-body img {
    background-color: transparent !important;
  }
  .markdown-body a { color: #2f81f7; }
  .markdown-body hr { background-color: #30363d; height: 1px; margin: 24px 0; }
  .markdown-body pre { background-color: #161b22; border: 1px solid #30363d; }
  .markdown-body table tr { background-color: #0d1117; }
  .markdown-body table tr:nth-child(2n) { background-color: #161b22; }
  .markdown-body table th, .markdown-body table td { border: 1px solid #30363d; }
</style>
</head>
<body>
<article class="markdown-body" id="content"></article>
<script>
  let raw = `__RAW_MARKDOWN__`;
  raw = raw.replace('screenshots/sdnflowguard-logo.png', '__LOGO_URI__');
  document.getElementById('content').innerHTML = marked.parse(raw);
</script>
</body>
</html>
"""

html_out = html_template.replace('__RAW_MARKDOWN__', js_readme).replace('__LOGO_URI__', js_logo)

preview_file = pathlib.Path('d:/Project/Nhom02_SDNFlowGuard/scratch/readme_preview.html')
preview_file.write_text(html_out, encoding='utf-8')

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
artifacts_dir = pathlib.Path(r"C:\Users\Admin\.gemini\antigravity\brain\f55b3611-32fe-47cd-9251-7af52f3afbcf")
preview_uri = preview_file.resolve().as_uri()

# Capture Desktop 1920x1080
out_desktop = artifacts_dir / "sdnflowguard_readme_desktop_1920.png"
subprocess.run([
    chrome_exe,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1920,1080",
    f"--screenshot={out_desktop}",
    preview_uri
], check=True)

# Capture Laptop 1366x768
out_laptop = artifacts_dir / "sdnflowguard_readme_laptop_1366.png"
subprocess.run([
    chrome_exe,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1366,768",
    f"--screenshot={out_laptop}",
    preview_uri
], check=True)

print("Both screenshots updated successfully.")
