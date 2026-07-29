
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    PARAGRAPH_TIMINGS_PATH, TIMELINE_OUTPUT_PATH,
    MIN_CLIP_DURATION_SECONDS, MAX_CLIPS_PER_PARAGRAPH,
    SEARCH_CANDIDATES_PER_PARAGRAPH
)
from timeline.builder import fill_paragraph_with_clips

with open(PARAGRAPH_TIMINGS_PATH) as f:
    paragraphs = json.load(f)

timeline = []
total_gap = 0.0

for p in paragraphs:
    idx = p["paragraph_index"]
    text = p["text"]
    start = p["start_seconds"]
    end = p["end_seconds"]

    if start is None or end is None:
        print(f"[{idx}] SKIPPED - unresolved timing")
        continue

    target_duration = end - start

    clips, covered = fill_paragraph_with_clips(
        paragraph_text=text,
        target_duration=target_duration,
        max_clips=MAX_CLIPS_PER_PARAGRAPH,
        candidates_to_fetch=SEARCH_CANDIDATES_PER_PARAGRAPH,
        min_clip_duration=MIN_CLIP_DURATION_SECONDS,
    )

    gap = target_duration - covered
    total_gap += max(0, gap)

    print(f"[{idx}] target={target_duration:.1f}s covered={covered:.1f}s clips={len(clips)} gap={gap:.1f}s")
    for c in clips:
        print(f"     -> \"{c[\'caption\']}\" ({c[\'use_duration_seconds\']:.1f}s, rel={c[\'relevance\']:.2f})")

    timeline.append({
        "paragraph_index": idx,
        "text": text,
        "narration_start_seconds": start,
        "narration_end_seconds": end,
        "target_duration_seconds": round(target_duration, 2),
        "covered_duration_seconds": round(covered, 2),
        "clips": clips,
    })

with open(TIMELINE_OUTPUT_PATH, "w") as f:
    json.dump(timeline, f, indent=2)

print(f"\nTotal uncovered gap across all paragraphs: {total_gap:.1f}s")
print(f"Saved timeline to {TIMELINE_OUTPUT_PATH}")
print("Done.")
