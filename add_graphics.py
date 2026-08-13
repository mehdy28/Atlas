
import os
import sys
import json
import glob
import shutil
import subprocess
import time

sys.path.append("/content/Atlas")

from config import (
    GRAPHICS_PLAN_TIMED_PATH, GRAPHICS_WORK_DIR, RENDER_WORK_DIR,
    GRAPHICS_DISPLAY_DURATION, BODY_FONT_PATH,
    NAVY_DEEP, GFX_WHITE, GFX_OFFWHITE, GFX_ORANGE,
    RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS,
    FINAL_VIDEO_PATH, PRODUCTION_DIR
)
from editor.overlay_renderer import render_all_graphics_single_pass
from editor.movis_setup import ensure_fonts_registered, hex_from_rgba
from editor.movis_styles import (
    render_text_box, render_stat_callout, render_bar_chart,
    render_list_reveal, render_comparison, render_line_chart, render_quote_card,
)
from editor.movis_renderer import export_alpha_clip

MOVIS_RENDERERS = {
    "text_box": render_text_box,
    "stat_callout": render_stat_callout,
    "bar_chart": render_bar_chart,
    "list_reveal": render_list_reveal,
    "comparison": render_comparison,
    "line_chart": render_line_chart,
    "quote_card": render_quote_card,
}

ensure_fonts_registered()

if os.path.exists(GRAPHICS_WORK_DIR):
    shutil.rmtree(GRAPHICS_WORK_DIR)
os.makedirs(GRAPHICS_WORK_DIR, exist_ok=True)

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
if not os.path.exists(silent_video_path):
    raise SystemExit("silent_full.mp4 not found. Run render_video.py first.")

with open(GRAPHICS_PLAN_TIMED_PATH) as f:
    graphics_plan = json.load(f)

palette = {
    "navy_hex": hex_from_rgba(NAVY_DEEP),
    "white_hex": hex_from_rgba(GFX_WHITE),
    "offwhite_hex": hex_from_rgba(GFX_OFFWHITE),
    "orange_hex": hex_from_rgba(GFX_ORANGE),
    "muted_blue_hex": "#5A78AA",
}
font_path = BODY_FONT_PATH
font_family = "Liberation Sans"

prepared = []
graphics_stage_start = time.time()

for i, g in enumerate(graphics_plan):
    _t0 = time.time()
    g_type = g["type"]

    renderer_fn = MOVIS_RENDERERS.get(g_type)
    if renderer_fn is None:
        print("Skipping graphic " + str(i) + ": no Movis renderer for type '" + g_type + "'")
        continue

    mov_path = os.path.join(GRAPHICS_WORK_DIR, "gfx_" + str(i).zfill(3) + ".mov")

    try:
        scene = renderer_fn(
            g.get("content", {}), duration=GRAPHICS_DISPLAY_DURATION, palette=palette,
            video_width=RENDER_WIDTH, video_height=RENDER_HEIGHT,
            font_path=font_path, font_family=font_family,
        )
    except Exception as e:
        print("FAILED building composition for graphic " + str(i) + " (" + g_type + "): " + str(e))
        continue

    ok = export_alpha_clip(scene, mov_path, fps=RENDER_FPS)
    if not ok:
        print("FAILED exporting graphic " + str(i) + " (" + g_type + ")")
        continue

    prepared.append({
        "mov_path": mov_path,
        "start_seconds": g["trigger_start_seconds"],
        "duration_seconds": GRAPHICS_DISPLAY_DURATION,
    })
    print("Graphic " + str(i) + ": " + g_type + " at " + str(g["trigger_start_seconds"]) + "s (" + str(round(time.time()-_t0,1)) + "s)")

print("\nAll graphics rendered in " + str(round(time.time()-graphics_stage_start,1)) + "s total (" + str(len(prepared)) + "/" + str(len(graphics_plan)) + " succeeded)")

if not prepared:
    print("No graphics succeeded - copying silent+audio video through without overlays.")
    composited_path = silent_video_path
else:
    compositing_start = time.time()
    print("\nCompositing " + str(len(prepared)) + " graphics in a single pass...")
    composited_path = os.path.join(GRAPHICS_WORK_DIR, "composited_full.mp4")
    ok, err = render_all_graphics_single_pass(silent_video_path, prepared, composited_path, RENDER_FPS, use_nvenc=True)
    if not ok:
        print("Single-pass compositing FAILED: " + err[:2000])
        raise SystemExit("Compositing failed.")
    print("Compositing succeeded in " + str(round(time.time()-compositing_start,1)) + "s")

audio_candidates = glob.glob(PRODUCTION_DIR + "/narration.*")
if not audio_candidates:
    raise SystemExit("No narration audio found in " + PRODUCTION_DIR)
audio_path = audio_candidates[0]

cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", composited_path, "-i", audio_path,
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "copy", "-c:a", "aac",
    FINAL_VIDEO_PATH,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Final audio mux FAILED: " + result.stderr[:1000])
    raise SystemExit("Final mux failed.")

print("\nFinal video with graphics saved to: " + FINAL_VIDEO_PATH)
print("Done.")
