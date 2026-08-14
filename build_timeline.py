
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    PARAGRAPH_TIMINGS_PATH, TIMELINE_OUTPUT_PATH,
    MIN_CLIP_DURATION_SECONDS, MAX_CLIPS_PER_PARAGRAPH,
    SEARCH_CANDIDATES_PER_PARAGRAPH, LOW_RELEVANCE_THRESHOLD, LOW_RELEVANCE_PARAGRAPHS_PATH
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
        "clips": clips,
        "avg_relevance": round(avg_relevance, 3),
    })

with open(TIMELINE_OUTPUT_PATH, "w") as f:
    json.dump(timeline, f, indent=2)

low_relevance = [p for p in timeline if p["avg_relevance"] < LOW_RELEVANCE_THRESHOLD]
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
