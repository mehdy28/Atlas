
import os
import sys
import sqlite3
from pathlib import Path
from tqdm import tqdm

sys.path.append("/content/Atlas")

from splitter.scene_detector import extract_thumbnail

DB_PATH = "/content/drive/MyDrive/AtlasData/atlas.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    SELECT scenes.id, assets.filepath, scenes.start_seconds, scenes.end_seconds, scenes.thumbnail_path
    FROM scenes
    JOIN assets ON scenes.asset_id = assets.id
    WHERE scenes.thumbnail_path IS NOT NULL
""")
rows = cur.fetchall()
conn.close()

print(f"Checking {len(rows)} expected thumbnails...")

missing = [r for r in rows if not os.path.exists(r[4])]
print(f"Missing: {len(missing)} | Already present: {len(rows) - len(missing)}")

regenerated = 0
failed = 0

for scene_id, video_path, start, end, thumb_path in tqdm(missing, desc="Regenerating thumbnails"):

    if not video_path or not os.path.exists(video_path):
        failed += 1
        continue

    midpoint = start + ((end - start) / 2)

    Path(os.path.dirname(thumb_path)).mkdir(parents=True, exist_ok=True)

    ok = extract_thumbnail(video_path, midpoint, thumb_path)
    if ok:
        regenerated += 1
    else:
        failed += 1

print(f"\nRegenerated: {regenerated} | Failed: {failed}")
