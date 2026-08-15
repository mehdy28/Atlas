
import os
import sys
import shutil
import sqlite3
import requests
import threading
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

sys.path.append("/content/Atlas")

from config import (
    THUMBNAIL_DIR, SCENE_THRESHOLD, MIN_SCENE_LEN_SECONDS,
    DRIVE_DB_PATH, SCENE_SPLIT_TEMP_DIR, MAX_ASSETS_PER_SPLIT_RUN, SPLIT_PARALLELISM
)
from splitter.scene_detector import detect_scenes, extract_thumbnail

Path(THUMBNAIL_DIR).mkdir(parents=True, exist_ok=True)
Path(SCENE_SPLIT_TEMP_DIR).mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DRIVE_DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(assets)")
cols = [r[1] for r in cur.fetchall()]
if "scenes_extracted" not in cols:
    cur.execute("ALTER TABLE assets ADD COLUMN scenes_extracted INTEGER DEFAULT 0")
    conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS scenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER, scene_index INTEGER, start_seconds REAL, end_seconds REAL,
    duration_seconds REAL, thumbnail_path TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(id)
)
""")
conn.commit()

cur.execute("SELECT id, url FROM assets WHERE scenes_extracted IS NULL OR scenes_extracted = 0 ORDER BY id ASC")
all_pending = cur.fetchall()
total_pending = len(all_pending)
pending = all_pending[:MAX_ASSETS_PER_SPLIT_RUN]
conn.close()

print("Total pending: " + str(total_pending) + " | Processing this run: " + str(len(pending)) + " (capped at " + str(MAX_ASSETS_PER_SPLIT_RUN) + ", " + str(SPLIT_PARALLELISM) + " parallel workers)")
if total_pending > len(pending):
    print("Remaining " + str(total_pending - len(pending)) + " assets picked up on a future run.")

db_lock = threading.Lock()
pbar = tqdm(total=len(pending), desc="Downloading + splitting")


def process_asset(asset_id, url):
    if not url:
        with db_lock:
            c = sqlite3.connect(DRIVE_DB_PATH)
            c.execute("UPDATE assets SET scenes_extracted = -1 WHERE id = ?", (asset_id,))
            c.commit()
            c.close()
        pbar.update(1)
        return

    ext = os.path.splitext(url.split("?")[0])[1] or ".mp4"
    temp_path = os.path.join(SCENE_SPLIT_TEMP_DIR, "asset_" + str(asset_id) + ext)

    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(temp_path, "wb") as f:
            for chunk in resp.iter_content(1024 * 1024):
                f.write(chunk)
    except Exception as e:
        with db_lock:
            c = sqlite3.connect(DRIVE_DB_PATH)
            c.execute("UPDATE assets SET scenes_extracted = -1 WHERE id = ?", (asset_id,))
            c.commit()
            c.close()
        pbar.update(1)
        return

    try:
        scenes = detect_scenes(temp_path, threshold=SCENE_THRESHOLD, min_scene_len_seconds=MIN_SCENE_LEN_SECONDS)
    except Exception:
        with db_lock:
            c = sqlite3.connect(DRIVE_DB_PATH)
            c.execute("UPDATE assets SET scenes_extracted = -1 WHERE id = ?", (asset_id,))
            c.commit()
            c.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        pbar.update(1)
        return

    scene_rows = []
    for idx, (start, end) in enumerate(scenes):
        duration = end - start
        midpoint = start + duration / 2
        thumb_filename = "asset" + str(asset_id) + "_scene" + str(idx) + ".jpg"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_filename)
        ok = extract_thumbnail(temp_path, midpoint, thumb_path)
        scene_rows.append((asset_id, idx, start, end, duration, thumb_path if ok else None))

    with db_lock:
        c = sqlite3.connect(DRIVE_DB_PATH)
        cc = c.cursor()
        cc.executemany("""
            INSERT INTO scenes(asset_id, scene_index, start_seconds, end_seconds, duration_seconds, thumbnail_path)
            VALUES (?,?,?,?,?,?)
        """, scene_rows)
        cc.execute("UPDATE assets SET scenes_extracted = 1 WHERE id = ?", (asset_id,))
        c.commit()
        c.close()

    if os.path.exists(temp_path):
        os.remove(temp_path)
    pbar.update(1)


with ThreadPoolExecutor(max_workers=SPLIT_PARALLELISM) as executor:
    futures = [executor.submit(process_asset, asset_id, url) for asset_id, url in pending]
    for f in futures:
        f.result()

pbar.close()
print("Done. No bulk video files retained on Drive.")
