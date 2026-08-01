
import os
import sys
import json
import glob
import shutil
import subprocess

sys.path.append("/content/Atlas")

from config import (
    GRAPHICS_PLAN_TIMED_PATH, GRAPHICS_WORK_DIR, RENDER_WORK_DIR,
    GRAPHICS_DISPLAY_DURATION, GRAPHICS_FADE_DURATION,
    GRAPHICS_MARGIN_X, GRAPHICS_MARGIN_Y,
    TITLE_FONT_PATH, BODY_FONT_PATH,
    CARD_BG_COLOR, CARD_ACCENT_COLOR, CARD_TEXT_COLOR, CARD_SUBTEXT_COLOR,
    CARD_ACCENT_WIDTH, CARD_CORNER_RADIUS,
    RENDER_WIDTH, RENDER_HEIGHT, RENDER_FPS,
    FINAL_VIDEO_PATH, PRODUCTION_DIR
)
from editor.graphics_cards import generate_card_image
from editor.overlay_renderer import render_alpha_clip, overlay_clip_onto_video

if os.path.exists(GRAPHICS_WORK_DIR):
    shutil.rmtree(GRAPHICS_WORK_DIR)
os.makedirs(GRAPHICS_WORK_DIR, exist_ok=True)

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
if not os.path.exists(silent_video_path):
    raise SystemExit("silent_full.mp4 not found. Run render_video.py first.")

with open(GRAPHICS_PLAN_TIMED_PATH) as f:
    graphics = json.load(f)

current_video = silent_video_path
applied = 0
failed = 0

for i, g in enumerate(graphics):
    png_path = os.path.join(GRAPHICS_WORK_DIR, "card_" + str(i).zfill(3) + ".png")
    mov_path = os.path.join(GRAPHICS_WORK_DIR, "card_" + str(i).zfill(3) + ".mov")

    width, height = generate_card_image(
        g, png_path, TITLE_FONT_PATH, BODY_FONT_PATH,
        CARD_BG_COLOR, CARD_ACCENT_COLOR, CARD_TEXT_COLOR, CARD_SUBTEXT_COLOR,
        CARD_ACCENT_WIDTH, CARD_CORNER_RADIUS
    )

    ok, err = render_alpha_clip(png_path, mov_path, GRAPHICS_DISPLAY_DURATION, GRAPHICS_FADE_DURATION, RENDER_FPS)
    if not ok:
        print("Card render FAILED for graphic " + str(i) + " (" + g["type"] + "): " + err[:300])
        failed += 1
        continue

    pos_x = GRAPHICS_MARGIN_X
    pos_y = RENDER_HEIGHT - height - GRAPHICS_MARGIN_Y

    output_path = os.path.join(GRAPHICS_WORK_DIR, "composited_" + str(i).zfill(3) + ".mp4")

    ok, err = overlay_clip_onto_video(
        current_video, mov_path, g["trigger_start_seconds"], GRAPHICS_DISPLAY_DURATION,
        pos_x, pos_y, output_path
    )
    if not ok:
        print("Overlay FAILED for graphic " + str(i) + " (" + g["type"] + "): " + err[:300])
        failed += 1
        continue

    current_video = output_path
    applied += 1
    print("Applied graphic " + str(i) + ": " + g["type"] + " at " + str(g["trigger_start_seconds"]) + "s")

print("\nApplied: " + str(applied) + " | Failed: " + str(failed))

audio_candidates = glob.glob(PRODUCTION_DIR + "/narration.*")
if not audio_candidates:
    raise SystemExit("No narration audio found in " + PRODUCTION_DIR)
audio_path = audio_candidates[0]

cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", current_video,
    "-i", audio_path,
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "copy", "-c:a", "aac",
    "-shortest",
    FINAL_VIDEO_PATH,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Final audio mux FAILED: " + result.stderr[:1000])
    raise SystemExit("Final mux failed.")

print("\nFinal video with graphics saved to: " + FINAL_VIDEO_PATH)
print("Done.")
