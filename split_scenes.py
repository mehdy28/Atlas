
import os
import sys
import sqlite3
from pathlib import Path
from tqdm import tqdm

sys.path.append("/content/Atlas")

from config import DB_PATH, THUMBNAIL_DIR, SCENE_THRESHOLD, MIN_SCENE_LEN_SECONDS
from splitter.scene_detector import detect_scenes, extract_thumbnail

Path(THUMBNAIL_DIR).mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# scenes_extracted: 0 = not done, 1 = done, -1 = failed (skip on retry)
cur.execute("PRAGMA table_info(assets)")
cols = [row[1] for row in cur.fetchall()]
if "scenes_extracted" not in cols:
    cur.execute("ALTER TABLE assets ADD COLUMN scenes_extracted INTEGER DEFAULT 0")
    conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    scene_index INTEGER,
    start_seconds REAL,
    end_seconds REAL,
    duration_seconds REAL,
    thumbnail_path TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(id)
)
""")
conn.commit()

cur.execute("SELECT COUNT(*) FROM assets")
total = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM assets WHERE scenes_extracted = 1")
done = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM assets WHERE scenes_extracted = -1")
failed = cur.fetchone()[0]

print(f"Total assets: {total} | Already done: {done} | Previously failed: {failed} | Remaining: {total - done - failed}")

cur.execute("""
    SELECT id, filepath FROM assets
    WHERE scenes_extracted IS NULL OR scenes_extracted = 0
""")
pending = cur.fetchall()

for asset_id, filepath in tqdm(pending, desc="Splitting scenes"):

    if not filepath or not os.path.exists(filepath):
        cur.execute("UPDATE assets SET scenes_extracted = -1 WHERE id = ?", (asset_id,))
        conn.commit()
        continue

    try:
        scenes = detect_scenes(
            filepath,
            threshold=SCENE_THRESHOLD,
            min_scene_len_seconds=MIN_SCENE_LEN_SECONDS
        )
    except Exception as e:
        print(f"Scene detection failed for asset {asset_id}: {e}")
        cur.execute("UPDATE assets SET scenes_extracted = -1 WHERE id = ?", (asset_id,))
        conn.commit()
        continue

    for idx, (start, end) in enumerate(scenes):
        duration = end - start
        midpoint = start + (duration / 2)

        thumb_filename = f"asset{asset_id}_scene{idx}.jpg"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_filename)

        ok = extract_thumbnail(filepath, midpoint, thumb_path)
        if not ok:
            thumb_path = None

        cur.execute("""
            INSERT INTO scenes(asset_id, scene_index, start_seconds, end_seconds, duration_seconds, thumbnail_path)
            VALUES (?,?,?,?,?,?)
        """, (asset_id, idx, start, end, duration, thumb_path))

    cur.execute("UPDATE assets SET scenes_extracted = 1 WHERE id = ?", (asset_id,))
    conn.commit()

conn.close()
print("\nDone.")
