import os
import math
from PIL import Image, ImageDraw

out_dir = r"D:\Project\Nhom02_SDNFlowGuard\frontend\public"

# ==============================================================================
# 1. GENERATE sdnflowguard-logo.svg (Full High-DPI Vector Logo for Header/Sidebar)
# ==============================================================================
# ViewBox 0 0 128 128
svg_logo = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="100%" height="100%">
  <defs>
    <!-- Outer Shield Stroke Gradient -->
    <linearGradient id="shieldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#0284c7" />
    </linearGradient>

    <!-- Shield Background Gradient -->
    <linearGradient id="shieldBg" x1="50%" y1="0%" x2="50%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="60%" stop-color="#0b1329" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>

    <!-- Glowing Core Gradient -->
    <linearGradient id="coreGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="50%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#0284c7" />
    </linearGradient>

    <!-- Subtle Circuit Trace Gradient -->
    <linearGradient id="traceGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284c7" />
      <stop offset="50%" stop-color="#00f0ff" />
      <stop offset="100%" stop-color="#38bdf8" />
    </linearGradient>
  </defs>

  <!-- Outer Shield Geometry -->
  <!-- Top crest: (64, 8), corners: (114, 24) and (14, 24), bottom tip: (64, 122) -->
  <path d="M 64,8 
           L 114,24 
           C 114,72 96,106 64,122 
           C 32,106 14,72 14,24 
           Z" 
        fill="url(#shieldBg)" 
        stroke="url(#shieldBorder)" 
        stroke-width="5" 
        stroke-linejoin="round" />

  <!-- Inner Shield Accent Rim -->
  <path d="M 64,15 
           L 106,28 
           C 106,68 90,98 64,112 
           C 38,98 22,68 22,28 
           Z" 
        fill="none" 
        stroke="#0284c7" 
        stroke-width="1.5" 
        stroke-opacity="0.45" />

  <!-- Network Circuit Traces (SDN Data Plane) -->
  <!-- Horizontal Bus -->
  <line x1="38" y1="64" x2="90" y2="64" stroke="url(#traceGrad)" stroke-width="2.5" stroke-linecap="round" />
  <!-- Vertical Bus -->
  <line x1="64" y1="36" x2="64" y2="92" stroke="url(#traceGrad)" stroke-width="2.5" stroke-linecap="round" />
  <!-- Diagonal Links -->
  <line x1="64" y1="64" x2="44" y2="44" stroke="url(#traceGrad)" stroke-width="2" stroke-linecap="round" />
  <line x1="64" y1="64" x2="84" y2="44" stroke="url(#traceGrad)" stroke-width="2" stroke-linecap="round" />
  <line x1="64" y1="64" x2="46" y2="84" stroke="url(#traceGrad)" stroke-width="2" stroke-linecap="round" />
  <line x1="64" y1="64" x2="82" y2="84" stroke="url(#traceGrad)" stroke-width="2" stroke-linecap="round" />

  <!-- Peripheral SDN Switch Nodes -->
  <circle cx="44" cy="44" r="4.5" fill="#0b1329" stroke="#00f0ff" stroke-width="2" />
  <circle cx="84" cy="44" r="4.5" fill="#0b1329" stroke="#00f0ff" stroke-width="2" />
  <circle cx="46" cy="84" r="4" fill="#0b1329" stroke="#38bdf8" stroke-width="2" />
  <circle cx="82" cy="84" r="4" fill="#0b1329" stroke="#38bdf8" stroke-width="2" />
  
  <circle cx="64" cy="36" r="3.5" fill="#00f0ff" />
  <circle cx="64" cy="92" r="3.5" fill="#00f0ff" />
  <circle cx="38" cy="64" r="3.5" fill="#00f0ff" />
  <circle cx="90" cy="64" r="3.5" fill="#00f0ff" />

  <!-- Central Controller Core (ONOS / Security Engine) -->
  <circle cx="64" cy="64" r="14" fill="#0f172a" stroke="url(#shieldBorder)" stroke-width="2.5" />
  <circle cx="64" cy="64" r="9" fill="url(#coreGlow)" />
  <circle cx="64" cy="64" r="4" fill="#ffffff" />
</svg>
"""

# ==============================================================================
# 2. GENERATE favicon.svg (Optical-sized vector specifically for 16-32px tabs)
# ==============================================================================
# In a 32x32 viewBox, maximize the shield to 30x30 so there is no wasted padding!
# High-contrast bold borders (3px) and high-visibility cyan core
svg_favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="100%" height="100%">
  <defs>
    <linearGradient id="favShieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="100%" stop-color="#00f0ff" />
    </linearGradient>
  </defs>
  <!-- Full-bleed Shield Outline (Optical Sizing: bold, clear, high contrast) -->
  <path d="M 16,1 
           L 29,5 
           C 29,19 24,27 16,31 
           C 8,27 3,19 3,5 
           Z" 
        fill="#0a1329" 
        stroke="url(#favShieldGrad)" 
        stroke-width="2.6" 
        stroke-linejoin="round" />

  <!-- Inner Cyan Defense Accent -->
  <!-- Cross Connectors -->
  <line x1="9" y1="16" x2="23" y2="16" stroke="#00f0ff" stroke-width="2" stroke-linecap="round" />
  <line x1="16" y1="9" x2="16" y2="23" stroke="#00f0ff" stroke-width="2" stroke-linecap="round" />

  <!-- 4 Corner SDN Node Dots -->
  <circle cx="11" cy="11" r="2.2" fill="#38bdf8" />
  <circle cx="21" cy="11" r="2.2" fill="#38bdf8" />
  <circle cx="11" cy="21" r="2.2" fill="#0284c7" />
  <circle cx="21" cy="21" r="2.2" fill="#0284c7" />

  <!-- Central Glowing Controller Core -->
  <circle cx="16" cy="16" r="4.5" fill="#00f0ff" />
  <circle cx="16" cy="16" r="2.2" fill="#ffffff" />
</svg>
"""

with open(os.path.join(out_dir, "sdnflowguard-logo.svg"), "w", encoding="utf-8") as f:
    f.write(svg_logo.strip())
print("Saved sdnflowguard-logo.svg")

with open(os.path.join(out_dir, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_favicon.strip())
print("Saved favicon.svg")
