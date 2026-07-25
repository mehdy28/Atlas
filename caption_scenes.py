
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


def safe_load_db():
    """
    Never blindly trust or overwrite. Only pull Drive down to local if
    Drive genuinely looks like the better copy (bigger, and has the
    tables we expect). Otherwise, refuse and let the human decide.
    """
    drive_exists = os.path.exists(DRIVE_DB_PATH)
    local_exists = os.path.exists(LOCAL_DB_PATH)

    if not drive_exists and not local_exists:
        raise SystemExit("No DB found on Drive or locally. Run Module 1 and 2 first.")

    drive_size = os.path.getsize(DRIVE_DB_PATH) if drive_exists else 0
    local_size = os.path.getsize(LOCAL_DB_PATH) if local_exists else 0

    print(f"Drive DB: {drive_size/1024:.1f} KB | Local DB: {local_size/1024:.1f} KB")

    if local_exists and local_size > drive_size:
        print("WARNING: local copy is larger than Drive copy. Keeping local, NOT overwriting.")
        print("You may want to manually sync local -> Drive after this run.")
        return

    if drive_exists:
        shutil.copy2(DRIVE_DB_PATH, LOCAL_DB_PATH)
        print(f"Loaded Drive copy to local ({drive_size/1024:.1f} KB).")


safe_load_db()

conn = sqlite3.connect(LOCAL_DB_PATH)
cur = conn.cursor()

# Hard guard: refuse to proceed if the scenes table is missing entirely,
# instead of silently creating an empty one and masking data loss.
cur.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'scenes\'")
if cur.fetchone() is None:
    conn.close()
    raise SystemExit(
        "scenes table not found in the loaded DB. Refusing to proceed - "
        "this usually means Module 2 has not run successfully yet, or the "
        "wrong DB got loaded. Re-check before running this script again."
    )

cur.execute("PRAGMA table_info(scenes)")
cols = [row[1] for row in cur.fetchall()]
if "caption" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN caption TEXT")
if "caption_status" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN caption_status TEXT DEFAULT \'pending\'")
conn.commit()

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
            print(f"Checkpoint synced. Drive size now: {os.path.getsize(DRIVE_DB_PATH)/1024:.1f} KB")
            batches_since_sync = 0

finally:
    conn.commit()
    sync_to_drive()
    conn.close()
    print(f"\nFinal sync to Drive. DB size: {os.path.getsize(DRIVE_DB_PATH)/1024:.1f} KB")

print("Done.")
