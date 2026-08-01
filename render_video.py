
import os
import sys
import json
import glob
import shutil
import subprocess

sys.path.append("/content/Atlas")

from config import (
    EDITED_TIMELINE_PATH, RENDER_WORK_DIR, RENDER_WIDTH, RENDER_HEIGHT,
    RENDER_FPS, FINAL_VIDEO_PATH, PRODUCTION_DIR,
    GRADE_CONTRAST, GRADE_SATURATION, GRADE_BRIGHTNESS, GRADE_VIGNETTE_STRENGTH
)
from renderer.clip_renderer import render_clip, freeze_extend_clip

if os.path.exists(RENDER_WORK_DIR):
    shutil.rmtree(RENDER_WORK_DIR)
os.makedirs(RENDER_WORK_DIR, exist_ok=True)

with open(EDITED_TIMELINE_PATH) as f:
    timeline = json.load(f)

ordered_clip_paths = []
failures = []
seq = 0

for paragraph in timeline:
    p_idx = paragraph["paragraph_index"]
    clips = paragraph["clips"]
    target = paragraph["target_duration_seconds"]
    covered = paragraph["covered_duration_seconds"]
    gap = round(target - covered, 2)

    paragraph_clip_paths = []

    for clip in clips:
        out_path = os.path.join(RENDER_WORK_DIR, "clip_" + str(seq).zfill(4) + ".mp4")
        ok, err = render_clip(
            video_path=clip["video_path"],
            source_start=clip["source_start_seconds"],
            use_duration=clip["use_duration_seconds"],
            motion=clip["motion"],
            output_path=out_path,
            width=RENDER_WIDTH, height=RENDER_HEIGHT, fps=RENDER_FPS,
            grade_contrast=GRADE_CONTRAST, grade_saturation=GRADE_SATURATION,
            grade_brightness=GRADE_BRIGHTNESS, grade_vignette=GRADE_VIGNETTE_STRENGTH,
        )
        if not ok:
            print("FAILED clip render (paragraph " + str(p_idx) + "): " + err[:300])
            failures.append((p_idx, clip["scene_id"], err))
        else:
            paragraph_clip_paths.append(out_path)
        seq += 1

    if paragraph_clip_paths and gap > 0.05:
        last_clip_path = paragraph_clip_paths[-1]
        extended_path = last_clip_path.replace(".mp4", "_ext.mp4")
        ok, err = freeze_extend_clip(last_clip_path, extended_path, gap, RENDER_FPS)
        if ok:
            paragraph_clip_paths[-1] = extended_path
            print("Paragraph " + str(p_idx) + ": extended last clip by " + str(gap) + "s to close gap.")
        else:
            print("Paragraph " + str(p_idx) + ": freeze-extend FAILED: " + err[:300])

    ordered_clip_paths.extend(paragraph_clip_paths)
    print("Paragraph " + str(p_idx) + " rendered: " + str(len(paragraph_clip_paths)) + " clips.")

print("\nTotal clips rendered: " + str(len(ordered_clip_paths)) + " | Failures: " + str(len(failures)))

if not ordered_clip_paths:
    raise SystemExit("No clips rendered successfully. Aborting.")

filelist_path = os.path.join(RENDER_WORK_DIR, "filelist.txt")
with open(filelist_path, "w") as f:
    for p in ordered_clip_paths:
        f.write("file \'" + os.path.abspath(p) + "\'\n")

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "concat", "-safe", "0",
    "-i", filelist_path,
    "-c", "copy",
    silent_video_path,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Concat FAILED: " + result.stderr[:1000])
    raise SystemExit("Concat step failed.")

print("Concatenated silent video created.")

audio_candidates = glob.glob(PRODUCTION_DIR + "/narration.*")
if not audio_candidates:
    raise SystemExit("No narration audio found in " + PRODUCTION_DIR)
audio_path = audio_candidates[0]

cmd = [
    "ffmpeg", "-y", "-loglevel", "error",
    "-i", silent_video_path,
    "-i", audio_path,
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "copy", "-c:a", "aac",
    "-shortest",
    FINAL_VIDEO_PATH,
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Audio mux FAILED: " + result.stderr[:1000])
    raise SystemExit("Audio mux step failed.")

print("\nFinal video saved to: " + FINAL_VIDEO_PATH)
print("Done.")
