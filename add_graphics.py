
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
from editor.template_renderer import MotionTemplateRenderer
from editor.template_selector import select_and_build_sequence

# Movis renderers replaced by MotionTemplateRenderer

# Fonts handled by HTML/CSS motion engine

if os.path.exists(GRAPHICS_WORK_DIR):
    shutil.rmtree(GRAPHICS_WORK_DIR)
os.makedirs(GRAPHICS_WORK_DIR, exist_ok=True)

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
if not os.path.exists(silent_video_path):
    raise SystemExit("silent_full.mp4 not found. Run render_video.py first.")

with open(GRAPHICS_PLAN_TIMED_PATH) as f:
    graphics_plan = json.load(f)

# Styling handled by MotionTemplateRenderer

prepared = []
graphics_stage_start = time.time()

renderer = MotionTemplateRenderer(RENDER_WIDTH, RENDER_HEIGHT)
renderer.start()

try:
    for i, g in enumerate(graphics_plan):
        _t0 = time.time()
        g_type = g["type"]

        try:
            sequence, meta = select_and_build_sequence(g)
        except Exception as e:
            print(f"FAILED selecting template for graphic {i} ({g_type}): {e}")
            continue

        mov_path = os.path.join(GRAPHICS_WORK_DIR, "gfx_" + str(i).zfill(3) + ".mov")

        try:
            ok = renderer.render_sequence_to_mov(sequence, mov_path, fps=RENDER_FPS, transparent=True)
        except Exception as e:
            print(f"FAILED rendering graphic {i} ({g_type}): {e}")
            continue

        if not ok or not os.path.exists(mov_path):
            print(f"FAILED exporting graphic {i} ({g_type})")
            continue

        actual_duration = sequence.duration
        prepared.append({
            "mov_path": mov_path,
            "start_seconds": g["trigger_start_seconds"],
            "duration_seconds": actual_duration,
        })
        print(f"Graphic {i}: {g_type} -> {meta.get('id')} at {g['trigger_start_seconds']}s, dur={round(actual_duration,1)}s ({round(time.time()-_t0,1)}s)")
finally:
    renderer.close()

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
