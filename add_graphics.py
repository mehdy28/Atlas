
import os
import sys
import json
import glob
import shutil
import subprocess

sys.path.append("/content/Atlas")

from config import (
    GRAPHICS_PLAN_TIMED_PATH, GRAPHICS_WORK_DIR, RENDER_WORK_DIR,
    GRAPHICS_DISPLAY_DURATION,
    TITLE_FONT_PATH, BODY_FONT_PATH, BODY_FONT_REGULAR_PATH, SERIF_FONT_PATH,
    NAVY_DEEP, NAVY_PANEL, GFX_WHITE, GFX_OFFWHITE, GFX_ORANGE, GFX_SHADOW,
    RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS,
    FINAL_VIDEO_PATH, PRODUCTION_DIR
)
from editor.graphics_styles import select_style_fn
from editor.overlay_renderer import render_graphic_alpha_clip, render_all_graphics_single_pass

if os.path.exists(GRAPHICS_WORK_DIR):
    shutil.rmtree(GRAPHICS_WORK_DIR)
os.makedirs(GRAPHICS_WORK_DIR, exist_ok=True)

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
if not os.path.exists(silent_video_path):
    raise SystemExit("silent_full.mp4 not found. Run render_video.py first.")

with open(GRAPHICS_PLAN_TIMED_PATH) as f:
    graphics_plan = json.load(f)

fonts = {"title": TITLE_FONT_PATH, "bold": BODY_FONT_PATH, "reg": BODY_FONT_REGULAR_PATH, "serif": SERIF_FONT_PATH}
palette = {
    "navy_deep": NAVY_DEEP, "navy_panel": NAVY_PANEL, "white": GFX_WHITE,
    "offwhite": GFX_OFFWHITE, "orange": GFX_ORANGE, "shadow": GFX_SHADOW,
}

prepared = []
for i, g in enumerate(graphics_plan):
    style_fn = select_style_fn(g)
    mov_path = os.path.join(GRAPHICS_WORK_DIR, "gfx_" + str(i).zfill(3) + ".mov")

    ok, err = render_graphic_alpha_clip(
        style_fn, g.get("content", {}), g, mov_path,
        RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS, GRAPHICS_DISPLAY_DURATION,
        fonts, palette
    )
    if not ok:
        print("FAILED rendering graphic " + str(i) + " (" + g["type"] + " / " + style_fn.__name__ + "): " + err[:400])
        continue

    prepared.append({
        "mov_path": mov_path,
        "start_seconds": g["trigger_start_seconds"],
        "duration_seconds": GRAPHICS_DISPLAY_DURATION,
    })
    print("Prepared graphic " + str(i) + ": " + g["type"] + " -> " + style_fn.__name__ + " at " + str(g["trigger_start_seconds"]) + "s")

print("\nCompositing " + str(len(prepared)) + " graphics in a single pass...")

composited_path = os.path.join(GRAPHICS_WORK_DIR, "composited_full.mp4")
ok, err = render_all_graphics_single_pass(silent_video_path, prepared, composited_path, RENDER_FPS)

if not ok:
    print("Single-pass compositing FAILED: " + err[:2000])
    raise SystemExit("Compositing failed.")

print("Compositing succeeded.")

audio_candidates = glob.glob(PRODUCTION_DIR + "/narration.*")
if not audio_candidates:
    raise SystemExit("No narration audio found in " + PRODUCTION_DIR)
audio_path = audio_candidates[0]

cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", composited_path,
    "-i", audio_path,
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
