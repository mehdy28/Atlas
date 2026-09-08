
import os
import sys
import json
import sqlite3

sys.path.append("/content/Atlas")

from config import (
    LOW_RELEVANCE_PARAGRAPHS_PATH, IMAGE_PROMPTS_PATH, GENERATED_IMAGES_DIR,
    SD_MODEL_NAME, IMAGE_GEN_STEPS, IMAGE_GEN_WIDTH, IMAGE_GEN_HEIGHT,
    GEMINI_API_KEY_PATH, GEMINI_MODEL_NAME, DRIVE_DB_PATH, IMAGE_DISPLAY_DURATION
)
from director.api_key_manager import get_or_prompt_api_key
from director.gemini_director import generate_image_prompts_batch
from editor.local_image_gen import generate_images_batch, unload_sd_pipeline

if not os.path.exists(LOW_RELEVANCE_PARAGRAPHS_PATH):
    print("No low_relevance_paragraphs.json found - nothing to generate images for.")
    raise SystemExit()

with open(LOW_RELEVANCE_PARAGRAPHS_PATH) as f:
    low_relevance = json.load(f)

if not low_relevance:
    print("No low-relevance paragraphs - skipping image generation.")
    raise SystemExit()

paragraphs_needing_images = [
    {"paragraph_index": p["paragraph_index"], "text": p["text"]}
    for p in low_relevance
]

print("Requesting image prompts for " + str(len(paragraphs_needing_images)) + " paragraph(s) in one batch...")
api_key = get_or_prompt_api_key(GEMINI_API_KEY_PATH)
prompts = generate_image_prompts_batch(paragraphs_needing_images, api_key, GEMINI_MODEL_NAME)

with open(IMAGE_PROMPTS_PATH, "w") as f:
    json.dump(prompts, f, indent=2)

print("Got " + str(len(prompts)) + " prompts. Generating images locally...")

results = generate_images_batch(
    prompts, GENERATED_IMAGES_DIR, SD_MODEL_NAME,
    steps=IMAGE_GEN_STEPS, width=IMAGE_GEN_WIDTH, height=IMAGE_GEN_HEIGHT
)

unload_sd_pipeline()

conn = sqlite3.connect(DRIVE_DB_PATH)
cur = conn.cursor()

for r in results:
    identifier = "generated_p" + str(r["paragraph_index"]) + "_" + str(abs(hash(r["prompt"])) % 100000)
    cur.execute("SELECT id FROM assets WHERE identifier=?", (identifier,))
    if cur.fetchone():
        continue

    cur.execute("""
        INSERT INTO assets(source, keyword, identifier, title, description,
                            duration_seconds, url, filepath, asset_type, scenes_extracted)
        VALUES (?,?,?,?,?,?,NULL,?,'image',1)
    """, ("stable_diffusion", "paragraph_" + str(r["paragraph_index"]), identifier,
          r["prompt"][:100], "", IMAGE_DISPLAY_DURATION, r["image_path"]))
    asset_id = cur.lastrowid

    cur.execute("""
        INSERT INTO scenes(asset_id, scene_index, start_seconds, end_seconds, duration_seconds, thumbnail_path, caption, caption_status)
        VALUES (?,0,0.0,?,?,?,?,'done')
    """, (asset_id, IMAGE_DISPLAY_DURATION, IMAGE_DISPLAY_DURATION, r["image_path"], r["prompt"]))

conn.commit()
conn.close()

print("\\nInserted " + str(len(results)) + " generated images as searchable assets (caption = the prompt used).")
print("NEEDS_NEW_FOOTAGE=true")
print("Done.")
