
import sys
import json
import getpass

sys.path.append("/content/Atlas")

from config import SCRIPT_PATH, GRAPHICS_PLAN_PATH, GEMINI_MODEL_NAME
from director.gemini_director import generate_script_and_graphics

topic = input("Enter the video topic: ").strip()
api_key = getpass.getpass("Enter your Gemini API key (hidden input, from aistudio.google.com/apikey): ").strip()

print("\nCalling Gemini (" + GEMINI_MODEL_NAME + ")...")
result = generate_script_and_graphics(topic, api_key, GEMINI_MODEL_NAME)

paragraphs = result["paragraphs"]
graphics = result["graphics"]
dropped = result["dropped_graphics"]

script_text = "\n\n".join(p["text"] for p in sorted(paragraphs, key=lambda x: x["paragraph_index"]))
with open(SCRIPT_PATH, "w") as f:
    f.write(script_text)

with open(GRAPHICS_PLAN_PATH, "w") as f:
    json.dump(graphics, f, indent=2)

print("\nTitle: " + result["title"])
print("Paragraphs: " + str(len(paragraphs)))
print("Graphics cues (validated): " + str(len(graphics)))
print("Graphics cues dropped (bad phrase match or invalid type): " + str(len(dropped)))

print("\n--- Script preview ---")
for p in sorted(paragraphs, key=lambda x: x["paragraph_index"])[:3]:
    print("[" + str(p["paragraph_index"]) + "] " + p["text"][:100])

print("\n--- Graphics preview ---")
for g in graphics[:5]:
    print("paragraph " + str(g["paragraph_index"]) + " | " + g["type"] + " | trigger: \"" + g["trigger_phrase"] + "\"")
    print("   content: " + json.dumps(g["content"]))

if dropped:
    print("\nWARNING - dropped graphics (trigger phrase not found verbatim in paragraph):")
    for g in dropped[:5]:
        print("  ", g)

print("\nSaved script to " + SCRIPT_PATH)
print("Saved graphics plan to " + GRAPHICS_PLAN_PATH)
print("Done.")
