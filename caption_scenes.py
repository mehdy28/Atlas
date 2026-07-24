
import os
import sys
import shutil
import sqlite3
from pathlib import Path
from tqdm import tqdm

sys.path.append("/content/Atlas")

from config import (
    DRIVE_DB_PATH, LOCAL_DB_PATH,
    CAPTION_MIN_DURATION, CAPTION_MAX_DURATION,
    CAPTION_BATCH_SIZE, CAPTION_CHECKPOINT_EVERY_BATCHES
)
from captioner.vision_captioner import caption_batch


def sync_to_drive():
    tmp_path = DRIVE_DB_PATH + ".tmp"
    shutil.copy2(LOCAL_DB_PATH, tmp_path)
    os.replace(tmp_path, DRIVE_DB_PATH)


if os.path.exists(DRIVE_DB_PATH):
    shutil.copy2(DRIVE_DB_PATH, LOCAL_DB_PATH)
    print(f"Loaded existing DB from Drive ({os.path.getsize(DRIVE_DB_PATH)/1024:.1f} KB)")
else:
    raise SystemExit("No atlas.db found on Drive. Run Module 1 and 2 first.")

conn = sqlite3.connect(LOCAL_DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info(scenes)")
cols = [row[1] for row in cur.fetchall()]
if "caption" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN caption TEXT")
if "caption_status" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN caption_status TEXT DEFAULT \'pending\'")
conn.commit()

# Permanently skip out-of-range scenes so they never get reconsidered
cur.execute("""
    UPDATE scenes SET caption_status = \'skipped_duration\'
    WHERE (caption_status IS NULL OR caption_status = \'pending\')
    AND (duration_seconds < ? OR duration_seconds > ?)
""", (CAPTION_MIN_DURATION, CAPTION_MAX_DURATION))
conn.commit()

cur.execute("SELECT COUNT(*) FROM scenes")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM scenes WHERE caption_status = \'done\'")
done = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM scenes WHERE caption_status = \'skipped_duration\'")
skipped = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM scenes WHERE caption_status = \'failed\'")
failed = cur.fetchone()[0]

print(f"Total scenes: {total} | Done: {done} | Skipped (duration): {skipped} | Failed: {failed}")
print(f"Remaining to caption: {total - done - skipped - failed}")

cur.execute("""
    SELECT id, thumbnail_path FROM scenes
    WHERE (caption_status IS NULL OR caption_status = \'pending\')
    AND thumbnail_path IS NOT NULL
""")
pending = cur.fetchall()

batches_since_sync = 0

def process_batch(batch):
    ids = [row[0] for row in batch]
    paths = [row[1] for row in batch]

    missing_mask = [not os.path.exists(p) for p in paths]
    for scene_id, missing in zip(ids, missing_mask):
        if missing:
            cur.execute("UPDATE scenes SET caption_status = \'failed\' WHERE id = ?", (scene_id,))

    valid_pairs = [(i, p) for i, p, m in zip(ids, paths, missing_mask) if not m]
    if not valid_pairs:
        return

    valid_ids = [p[0] for p in valid_pairs]
    valid_paths = [p[1] for p in valid_pairs]

    try:
        captions = caption_batch(valid_paths)
    except Exception as e:
        print(f"Batch captioning failed: {e}")
        for scene_id in valid_ids:
            cur.execute("UPDATE scenes SET caption_status = \'failed\' WHERE id = ?", (scene_id,))
        return

    for scene_id, caption in zip(valid_ids, captions):
        if caption:
            cur.execute(
                "UPDATE scenes SET caption = ?, caption_status = \'done\' WHERE id = ?",
                (caption, scene_id)
            )
        else:
            cur.execute("UPDATE scenes SET caption_status = \'failed\' WHERE id = ?", (scene_id,))


try:
    for batch_start in tqdm(range(0, len(pending), CAPTION_BATCH_SIZE), desc="Captioning scenes"):
        batch = pending[batch_start: batch_start + CAPTION_BATCH_SIZE]
        process_batch(batch)
        conn.commit()

        batches_since_sync += 1
        if batches_since_sync >= CAPTION_CHECKPOINT_EVERY_BATCHES:
            sync_to_drive()
            batches_since_sync = 0

finally:
    conn.commit()
    sync_to_drive()
    conn.close()
    print(f"\nSynced to Drive. DB size: {os.path.getsize(DRIVE_DB_PATH)/1024:.1f} KB")

print("Done.")
