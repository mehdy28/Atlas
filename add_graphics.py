
import os
import sys
import json
import glob
import shutil
import subprocess

sys.path.append("/content/Atlas")

from config import (
    GRAPHICS_PLAN_TIMED_PATH, GRAPHICS_WORK_DIR, RENDER_WORK_DIR,
    GRAPHICS_DISPLAY_DURATION, GRAPHICS_FADE_DURATION, GRAPHICS_SLIDE_DURATION,
    TITLE_FONT_PATH, BODY_FONT_PATH,
    PANEL_WIDTH, PANEL_BG_COLOR, PANEL_ACCENT_COLOR, PANEL_TEXT_COLOR, PANEL_SUBTEXT_COLOR, PANEL_ACCENT_WIDTH,
    SCRIM_COLOR, SCRIM_TEXT_COLOR, SCRIM_SUBTEXT_COLOR, SCRIM_ACCENT_COLOR,
    RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS,
    FINAL_VIDEO_PATH, PRODUCTION_DIR
)
from editor.graphics_cards import generate_card_image
from editor.overlay_renderer import render_all_graphics_single_pass

if os.path.exists(GRAPHICS_WORK_DIR):
    shutil.rmtree(GRAPHICS_WORK_DIR)
os.makedirs(GRAPHICS_WORK_DIR, exist_ok=True)

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
if not os.path.exists(silent_video_path):
    raise SystemExit("silent_full.mp4 not found. Run render_video.py first.")

with open(GRAPHICS_PLAN_TIMED_PATH) as f:
    graphics_plan = json.load(f)

prepared = []
for i, g in enumerate(graphics_plan):
    png_path = os.path.join(GRAPHICS_WORK_DIR, "card_" + str(i).zfill(3) + ".png")
    enter_from_left = (i % 2 == 0)

    variant, w, h = generate_card_image(
        g, png_path, TITLE_FONT_PATH, BODY_FONT_PATH,
        PANEL_WIDTH, PANEL_BG_COLOR, PANEL_ACCENT_COLOR, PANEL_TEXT_COLOR, PANEL_SUBTEXT_COLOR, PANEL_ACCENT_WIDTH,
        SCRIM_COLOR, SCRIM_TEXT_COLOR, SCRIM_SUBTEXT_COLOR, SCRIM_ACCENT_COLOR,
        RENDER_WIDTH, RENDER_HEIGHT, enter_from_left
    )

    prepared.append({
        "png_path": png_path,
        "variant": variant,
        "start_seconds": g["trigger_start_seconds"],
        "panel_width": PANEL_WIDTH,
        "enter_from_left": enter_from_left,
    })
    print("Prepared graphic " + str(i) + ": " + g["type"] + " (" + variant + ") at " + str(g["trigger_start_seconds"]) + "s")

print("\nCompositing all " + str(len(prepared)) + " graphics in a single pass...")

composited_path = os.path.join(GRAPHICS_WORK_DIR, "composited_full.mp4")
ok, err = render_all_graphics_single_pass(
    silent_video_path, prepared, composited_path,
    RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS,
    GRAPHICS_DISPLAY_DURATION, GRAPHICS_FADE_DURATION, GRAPHICS_SLIDE_DURATION
)

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
