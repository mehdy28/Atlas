
import os
import sys
import json
import glob
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

sys.path.append("/content/Atlas")

from config import (
    EDITED_TIMELINE_PATH, RENDER_WORK_DIR, RENDER_WIDTH, RENDER_HEIGHT,
    RENDER_FPS, FINAL_VIDEO_PATH, PRODUCTION_DIR,
    GRADE_CONTRAST, GRADE_SATURATION, GRADE_BRIGHTNESS, GRADE_VIGNETTE_STRENGTH,
    CLIP_CACHE_DIR, CLIP_CACHE_MAX_BYTES, USE_NVENC, RENDER_PARALLELISM
)
from renderer.clip_renderer import render_clip, freeze_extend_clip
from collectors.asset_cache import get_or_download

if os.path.exists(RENDER_WORK_DIR):
    shutil.rmtree(RENDER_WORK_DIR)
os.makedirs(RENDER_WORK_DIR, exist_ok=True)

with open(EDITED_TIMELINE_PATH) as f:
    timeline = json.load(f)


def resolve_local_video(clip):
    existing = clip.get("video_path")
    if existing and os.path.exists(existing):
        return existing
    source_url = clip.get("source_url")
    if not source_url:
        raise RuntimeError("Clip has no usable video_path or source_url: " + str(clip.get("scene_id")))
    return get_or_download(clip["scene_id"], source_url, CLIP_CACHE_DIR, CLIP_CACHE_MAX_BYTES)


jobs = []
seq = 0
for paragraph in timeline:
    for clip in paragraph["clips"]:
        out_path = os.path.join(RENDER_WORK_DIR, "clip_" + str(seq).zfill(4) + ".mp4")
        jobs.append((seq, paragraph, clip, out_path))
        seq += 1


def do_render(job):
    idx, paragraph, clip, out_path = job
    try:
        local_video = resolve_local_video(clip)
    except Exception as e:
        return idx, out_path, False, str(e)

    ok, err = render_clip(
        video_path=local_video,
        source_start=clip["source_start_seconds"],
        use_duration=clip["use_duration_seconds"],
        motion=clip["motion"],
        output_path=out_path,
        width=RENDER_WIDTH, height=RENDER_HEIGHT, fps=RENDER_FPS,
        grade_contrast=GRADE_CONTRAST, grade_saturation=GRADE_SATURATION,
        grade_brightness=GRADE_BRIGHTNESS, grade_vignette=GRADE_VIGNETTE_STRENGTH,
        use_nvenc=USE_NVENC,
    )
    return idx, out_path, ok, err


results = {}
with ThreadPoolExecutor(max_workers=RENDER_PARALLELISM) as executor:
    for idx, out_path, ok, err in executor.map(do_render, jobs):
        results[idx] = (out_path, ok, err)
        status = "OK" if ok else "FAILED: " + str(err)[:200]
        print("Clip " + str(idx) + "/" + str(len(jobs)) + ": " + status)

ordered_clip_paths = []
seq2 = 0
for paragraph in timeline:
    p_idx = paragraph["paragraph_index"]
    target = paragraph["target_duration_seconds"]
    covered = paragraph["covered_duration_seconds"]
    gap = round(target - covered, 2)

    paragraph_paths = []
    for clip in paragraph["clips"]:
        out_path, ok, err = results[seq2]
        if ok:
            paragraph_paths.append(out_path)
        seq2 += 1

    if paragraph_paths and gap > 0.05:
        last_path = paragraph_paths[-1]
        extended_path = last_path.replace(".mp4", "_ext.mp4")
        ok, err = freeze_extend_clip(last_path, extended_path, gap, RENDER_FPS, use_nvenc=USE_NVENC)
        if ok:
            paragraph_paths[-1] = extended_path

    ordered_clip_paths.extend(paragraph_paths)
    print("Paragraph " + str(p_idx) + ": " + str(len(paragraph_paths)) + " clips assembled.")

print("\nTotal clips rendered: " + str(len(ordered_clip_paths)))

if not ordered_clip_paths:
    raise SystemExit("No clips rendered successfully.")

filelist_path = os.path.join(RENDER_WORK_DIR, "filelist.txt")
with open(filelist_path, "w") as f:
    for p in ordered_clip_paths:
        f.write("file \'" + os.path.abspath(p) + "\'\n")

silent_video_path = os.path.join(RENDER_WORK_DIR, "silent_full.mp4")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
       "-i", filelist_path, "-c", "copy", silent_video_path]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Concat FAILED: " + result.stderr[:1000])
    raise SystemExit("Concat step failed.")

print("Concatenated silent video created.")

audio_candidates = glob.glob(PRODUCTION_DIR + "/narration.*")
if not audio_candidates:
    raise SystemExit("No narration audio found.")
audio_path = audio_candidates[0]

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", silent_video_path, "-i", audio_path,
       "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", FINAL_VIDEO_PATH]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("Audio mux FAILED: " + result.stderr[:1000])
    raise SystemExit("Audio mux failed.")

print("\nFinal video saved to: " + FINAL_VIDEO_PATH)
print("Done.")
