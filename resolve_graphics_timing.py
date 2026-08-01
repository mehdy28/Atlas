
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    PRODUCTION_DIR, SCRIPT_PATH, WHISPER_WORDS_PATH,
    GRAPHICS_PLAN_PATH
)
from alignment.aligner import load_script_paragraphs, build_word_level_times, resolve_trigger_phrase_time

with open(WHISPER_WORDS_PATH) as f:
    whisper_words = json.load(f)
whisper_words = [tuple(w) for w in whisper_words]

paragraphs = load_script_paragraphs(SCRIPT_PATH)
word_times = build_word_level_times(paragraphs, whisper_words)

with open(GRAPHICS_PLAN_PATH) as f:
    graphics = json.load(f)

resolved = []
unresolved = []

for g in graphics:
    result = resolve_trigger_phrase_time(word_times, g["paragraph_index"], g["trigger_phrase"])
    if result is None:
        unresolved.append(g)
        continue

    start, end = result
    g["trigger_start_seconds"] = start
    g["trigger_end_seconds"] = end
    resolved.append(g)

print("Resolved: " + str(len(resolved)) + " | Unresolved: " + str(len(unresolved)))

for g in resolved:
    print("[p" + str(g["paragraph_index"]) + "] " + g["type"] + " @ " + str(g["trigger_start_seconds"]) + "s -> \"" + g["trigger_phrase"] + "\"")

if unresolved:
    print("\nWARNING - could not locate these phrases verbatim:")
    for g in unresolved:
        print("  [p" + str(g["paragraph_index"]) + "] " + g["type"] + ": \"" + g["trigger_phrase"] + "\"")

output_path = PRODUCTION_DIR + "/graphics_plan_timed.json"
with open(output_path, "w") as f:
    json.dump(resolved, f, indent=2)

print("\nSaved timed graphics plan to " + output_path)
print("Done.")
