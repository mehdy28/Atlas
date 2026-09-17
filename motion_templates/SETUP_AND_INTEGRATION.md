# Motion Templates — Master Integration & Setup Guide

This document is the official specification for connecting the **Motion Template Library** to your larger automated documentary/video generation software.

---

## 1. Physical Location in Repo

```text
Atlas/
└── motion_templates/
    ├── engine/
    │   └── motion_engine.py       # Core rendering functions, easing curves, Sequence class
    ├── registry/
    │   └── registry.json          # Machine-readable catalog used by the software
    ├── templates/                 # 25+ templates ready to be rendered
    │   ├── tpl_01_title_full.py
    │   ├── tpl_08_feature_full.py           # Template 1: Memo + Layoffs Stat
    │   ├── tpl_22_stat_split_full.py        # Template 2: $10B Robotaxi Split
    │   ├── tpl_23_feature_to_split_world.py # Template 3: Continuous 3D camera pan
    │   ├── tpl_24_breaking_ticker.py        # Breaking News Bottom Crawler
    │   └── tpl_25_broadcast_lowerthird.py   # Speaker Name Card Lower Third
    ├── states/                    # 63 atomic state files
    └── docs/
        └── INTEGRATION.md
```

---

## 2. The Two Operating Modes

Your video software can call templates in one of two modes:

### Mode 1: Standalone Graphic (No Underlying Video)
- **Flag**: `transparent=False` (Default)
- **Behavior**: Uses the signature **warm brown ambient gradient** with subtle orange and pink lighting highlights.
- **Use Case**: Title cards, full-screen chart reveals, intermissions, chapter dividers.

### Mode 2: Transparent Video Overlay (Over Footage / B-roll)
- **Flag**: `transparent=True`
- **Behavior**: Background is rendered 100% transparent (`rgba(0,0,0,0)`).
- **Format**: Playwright outputs transparent RGBA PNG bytes with straight alpha channel.
- **Use Case**: Lower thirds over interviewees, breaking news tickers, corner badges over B-roll.

---

## 3. How the Bigger Software Discovers and Renders Templates

### Step A: Load the Catalog
```python
import json

with open('motion_templates/registry/registry.json', 'r') as f:
    catalog = json.load(f)

# Find templates by category or family
overlay_templates = [t for t in catalog['templates'] if t.get('family') == 'overlay']
```

### Step B: Python Function to Render Any Template to Video
```python
import sys, os, subprocess
from playwright.async_api import async_playwright

# Add template library to Python path
sys.path.insert(0, 'motion_templates/engine')
sys.path.insert(0, 'motion_templates/templates')

async def render_motion_template(template_id, output_mp4, duration=5.0, fps=30, transparent=False):
    mod = __import__(template_id)
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'png', '-r', str(fps), '-i', '-',
        '-c:v', 'libx264', '-pix_fmt', 'yuva420p' if transparent else 'yuv420p',
        '-crf', '18', '-preset', 'veryfast', output_mp4
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        total_frames = int(duration * fps)
        for f in range(total_frames):
            t = f / float(fps)
            if hasattr(mod, 'render_html'):
                html = mod.render_html(t, duration=duration, transparent=transparent)
            else:
                seq = mod.build_sequence()
                from motion_engine import wrap_frame
                html = wrap_frame(seq.html_at(t), transparent=transparent)
            await page.set_content(html)
            png_bytes = await page.screenshot(type='png', omit_background=transparent)
            proc.stdin.write(png_bytes)
        await browser.close()
    proc.stdin.close()
    proc.wait()
    return output_mp4
```

---

## 4. Compositing Over Footage in Your Automated Software

```bash
ffmpeg -y -i background.mp4 -i overlay.webm -filter_complex '[0:v][1:v]overlay=0:0:enable=\'between(t, 2.0, 7.0)\'[v]' -map '[v]' -c:v libx264 -pix_fmt yuv420p final.mp4
```