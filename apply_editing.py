
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    TIMELINE_OUTPUT_PATH, EDITED_TIMELINE_PATH,
    KEN_BURNS_MIN_ZOOM, KEN_BURNS_MAX_ZOOM, KEN_BURNS_MAX_PAN_FRACTION,
    CROSSFADE_DURATION_SECONDS, MIN_DURATION_FOR_PAN
)
from editor.motion import assign_motion_effect

with open(TIMELINE_OUTPUT_PATH) as f:
    timeline = json.load(f)

total_clips = 0

for paragraph in timeline:
    clips = paragraph["clips"]
    n_clips = len(clips)

    for i, clip in enumerate(clips):
        duration = clip["use_duration_seconds"]

        effect = assign_motion_effect(
            scene_id=clip["scene_id"],
            duration_seconds=duration,
            min_zoom=KEN_BURNS_MIN_ZOOM,
            max_zoom=KEN_BURNS_MAX_ZOOM,
            max_pan_fraction=KEN_BURNS_MAX_PAN_FRACTION,
            min_duration_for_pan=MIN_DURATION_FOR_PAN,
        )
        clip["motion"] = effect

        clip["transition_in_seconds"] = CROSSFADE_DURATION_SECONDS if i > 0 else 0.0
        clip["transition_out_seconds"] = CROSSFADE_DURATION_SECONDS if i < n_clips - 1 else 0.0

        total_clips += 1

with open(EDITED_TIMELINE_PATH, "w") as f:
    json.dump(timeline, f, indent=2)

print("Applied motion effects to " + str(total_clips) + " clips across " + str(len(timeline)) + " paragraphs.")
print("Saved edited timeline to " + EDITED_TIMELINE_PATH)
print("Done.")
