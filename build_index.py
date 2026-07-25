
import os
import sys
import shutil
import sqlite3
import numpy as np
import faiss

sys.path.append("/content/Atlas")

from config import (
    DRIVE_DB_PATH, LOCAL_DB_PATH,
    FAISS_INDEX_PATH, FAISS_IDS_PATH,
    EMBED_BATCH_SIZE
)
from search.embedder import embed_texts


def sync_to_drive():
    tmp_path = DRIVE_DB_PATH + ".tmp"
    shutil.copy2(LOCAL_DB_PATH, tmp_path)
    os.replace(tmp_path, DRIVE_DB_PATH)


def safe_load_db():
    drive_exists = os.path.exists(DRIVE_DB_PATH)
    local_exists = os.path.exists(LOCAL_DB_PATH)

    if not drive_exists and not local_exists:
        raise SystemExit("No DB found. Run earlier modules first.")

    drive_size = os.path.getsize(DRIVE_DB_PATH) if drive_exists else 0
    local_size = os.path.getsize(LOCAL_DB_PATH) if local_exists else 0

    if local_exists and local_size > drive_size:
        print(f"WARNING: local ({local_size/1024:.1f}KB) > Drive ({drive_size/1024:.1f}KB). Keeping local.")
        return

    shutil.copy2(DRIVE_DB_PATH, LOCAL_DB_PATH)
    print(f"Loaded Drive copy to local ({drive_size/1024:.1f} KB).")


safe_load_db()

conn = sqlite3.connect(LOCAL_DB_PATH)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scenes'")
if cur.fetchone() is None:
    conn.close()
    raise SystemExit("scenes table not found. Run Module 2 and 3 first.")

# Add usage-tracking columns needed for scoring, if not present
cur.execute("PRAGMA table_info(scenes)")
cols = [row[1] for row in cur.fetchall()]
if "times_used" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN times_used INTEGER DEFAULT 0")
if "last_used_at" not in cols:
    cur.execute("ALTER TABLE scenes ADD COLUMN last_used_at TEXT")
conn.commit()

cur.execute("""
    SELECT id, caption FROM scenes
    WHERE caption_status = \'done\' AND caption IS NOT NULL
    ORDER BY id
""")
rows = cur.fetchall()
conn.close()

if not rows:
    raise SystemExit("No captioned scenes found. Run Module 3 first.")

scene_ids = np.array([r[0] for r in rows], dtype=np.int64)
captions = [r[1] for r in rows]

print(f"Embedding {len(captions)} captions...")
embeddings = embed_texts(captions, batch_size=EMBED_BATCH_SIZE)
print(f"Embeddings shape: {embeddings.shape}")

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors = cosine similarity
index.add(embeddings.astype(np.float32))

print(f"FAISS index built with {index.ntotal} vectors, dim={dim}")

# Save index and id mapping locally first, then push to Drive
local_index_path = "/content/atlas_local.faiss"
local_ids_path = "/content/atlas_local_faiss_ids.npy"

faiss.write_index(index, local_index_path)
np.save(local_ids_path, scene_ids)

shutil.copy2(local_index_path, FAISS_INDEX_PATH)
shutil.copy2(local_ids_path, FAISS_IDS_PATH)

sync_to_drive()  # scenes table got new columns, push that too

print(f"\nSaved FAISS index to {FAISS_INDEX_PATH}")
print(f"Saved ID mapping to {FAISS_IDS_PATH}")
print("Done.")
