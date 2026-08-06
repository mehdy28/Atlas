
import sys
import json

sys.path.append("/content/Atlas")

from config import (
    SCRIPT_PATH, GRAPHICS_PLAN_PATH, GEMINI_MODEL_NAME,
    GEMINI_API_KEY_PATH, TARGET_VIDEO_MINUTES, WORDS_PER_MINUTE
)
from director.api_key_manager import get_or_prompt_api_key
from director.gemini_director import generate_script_and_graphics

api_key = get_or_prompt_api_key(GEMINI_API_KEY_PATH)

topic = input("Enter the video topic: ").strip()

minutes_input = input("Target video length in minutes (default " + str(TARGET_VIDEO_MINUTES) + "): ").strip()
target_minutes = int(minutes_input) if minutes_input else TARGET_VIDEO_MINUTES

print("\nCalling Gemini (" + GEMINI_MODEL_NAME + ") for a ~" + str(target_minutes) + " minute script...")
result = generate_script_and_graphics(
    topic, api_key, GEMINI_MODEL_NAME,
    target_minutes=target_minutes, words_per_minute=WORDS_PER_MINUTE
)

paragraphs = result["paragraphs"]
graphics = result["graphics"]
dropped = result["dropped_graphics"]

script_text = "\n\n".join(p["text"] for p in sorted(paragraphs, key=lambda x: x["paragraph_index"]))
with open(SCRIPT_PATH, "w") as f:
    f.write(script_text)

with open(GRAPHICS_PLAN_PATH, "w") as f:
    json.dump(graphics, f, indent=2)

word_count = len(script_text.split())

print("\nTitle: " + result["title"])
print("Paragraphs: " + str(len(paragraphs)))
print("Word count: " + str(word_count) + " (~" + str(round(word_count/WORDS_PER_MINUTE,1)) + " min at " + str(WORDS_PER_MINUTE) + " wpm)")
print("Graphics cues (validated): " + str(len(graphics)))
print("Graphics cues dropped: " + str(len(dropped)))

print("\n--- Script preview ---")
for p in sorted(paragraphs, key=lambda x: x["paragraph_index"])[:3]:
    print("[" + str(p["paragraph_index"]) + "] " + p["text"][:100])

print("\n--- Graphics type distribution ---")
from collections import Counter
type_counts = Counter(g["type"] for g in graphics)
for t, c in type_counts.most_common():
    print("  " + t + ": " + str(c))

if dropped:
    print("\nWARNING - dropped graphics (trigger phrase not found verbatim):")
    for g in dropped[:5]:
        print("  ", g)

print("\nSaved script to " + SCRIPT_PATH)
print("Saved graphics plan to " + GRAPHICS_PLAN_PATH)
print("Done.")
