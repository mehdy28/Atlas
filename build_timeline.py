import json
from config import FOOTAGE_KEYWORDS_PATH
try:
    with open(FOOTAGE_KEYWORDS_PATH) as _fk: footage_keywords = json.load(_fk)
except: footage_keywords = []

import sys
import json

sys.path.append("/content/Atlas")

import os
from config import (
    PARAGRAPH_TIMINGS_PATH, TIMELINE_OUTPUT_PATH,
    MIN_CLIP_DURATION_SECONDS, MAX_CLIPS_PER_PARAGRAPH,
    SEARCH_CANDIDATES_PER_PARAGRAPH, LOW_RELEVANCE_THRESHOLD, LOW_RELEVANCE_PARAGRAPHS_PATH,
    PARAGRAPH_QUERY_OVERRIDES_PATH
)

query_overrides = {}
if os.path.exists(PARAGRAPH_QUERY_OVERRIDES_PATH):
    with open(PARAGRAPH_QUERY_OVERRIDES_PATH) as f:
        query_overrides = json.load(f)
from timeline.builder import fill_paragraph_with_clips

with open(PARAGRAPH_TIMINGS_PATH) as f:
    paragraphs = json.load(f)

timeline = []
total_gap = 0.0
global_used_scenes = set()

for p in paragraphs:
    idx = p["paragraph_index"]
    text = p["text"]
    start = p["start_seconds"]
    end = p["end_seconds"]

    if start is None or end is None:
        print(f"[{idx}] SKIPPED - unresolved timing")
        continue

    target_duration = end - start

    search_text = query_overrides.get(str(idx), text)
    search_text = query_overrides.get(str(idx), text)
    clips, covered, uncovered = fill_paragraph_with_clips(
        paragraph_text=search_text,
        target_duration=target_duration,
        max_clips=MAX_CLIPS_PER_PARAGRAPH,
        candidates_to_fetch=SEARCH_CANDIDATES_PER_PARAGRAPH,
        min_clip_duration=MIN_CLIP_DURATION_SECONDS,
        exclude_scene_ids=global_used_scenes,
    )

    # Fallback to visual keywords if the abstract sentence found no clips
    if covered < 2.0 and "footage_keywords" in globals():
        fallback_kw = footage_keywords[idx % len(footage_keywords)]
        extra_clips, extra_cov, _ = fill_paragraph_with_clips(
            paragraph_text=fallback_kw,
            target_duration=target_duration - covered,
            max_clips=MAX_CLIPS_PER_PARAGRAPH - len(clips),
            candidates_to_fetch=SEARCH_CANDIDATES_PER_PARAGRAPH,
            min_clip_duration=MIN_CLIP_DURATION_SECONDS,
            exclude_scene_ids=global_used_scenes,
        )
        clips.extend(extra_clips)
        covered += extra_cov
        uncovered = max(0.0, target_duration - covered)

    for c in clips:
        global_used_scenes.add(c["scene_id"])

    gap = target_duration - covered
    total_gap += max(0, gap)

    print(f"[{idx}] target={target_duration:.1f}s covered={covered:.1f}s clips={len(clips)} gap={gap:.1f}s")
    for c in clips:
        caption = c["caption"]
        clip_dur = c["use_duration_seconds"]
        clip_rel = c["relevance"]
        line = "     -> " + repr(caption) + " (" + str(round(clip_dur, 1)) + "s, rel=" + str(round(clip_rel, 2)) + ")"
        print(line)

    avg_relevance = sum(c["relevance"] for c in clips) / len(clips) if clips else 0.0

    timeline.append({
        "paragraph_index": idx,
        "text": text,
        "narration_start_seconds": start,
        "narration_end_seconds": end,
        "target_duration_seconds": round(target_duration, 2),
        "covered_duration_seconds": round(covered, 2),
        "uncovered_seconds": uncovered,
        "clips": clips,
        "avg_relevance": round(avg_relevance, 3),
    })

with open(TIMELINE_OUTPUT_PATH, "w") as f:
    json.dump(timeline, f, indent=2)

# Flag any paragraph with a real uncovered gap OR low average relevance -
# strict per-clip gating means a gap can exist even when the clips that
# WERE selected are individually high-quality.
low_relevance = [p for p in timeline if p["uncovered_seconds"] > 0.5 or p["avg_relevance"] < LOW_RELEVANCE_THRESHOLD]
with open(LOW_RELEVANCE_PARAGRAPHS_PATH, "w") as f:
    json.dump(low_relevance, f, indent=2)

if low_relevance:
    print("\n" + str(len(low_relevance)) + " paragraph(s) below relevance threshold (" + str(LOW_RELEVANCE_THRESHOLD) + "):")
    for p in low_relevance:
        print("  [p" + str(p["paragraph_index"]) + "] avg_relevance=" + str(p["avg_relevance"]) + " | " + p["text"][:70])
else:
    print("\nAll paragraphs met the relevance threshold - no boost round needed.")

print("\nTotal uncovered gap across all paragraphs: " + str(round(total_gap, 1)) + "s")
print("Saved timeline to " + TIMELINE_OUTPUT_PATH)
print("Done.")
