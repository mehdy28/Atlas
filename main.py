import os
import sys
import sqlite3

sys.path.append("/content/Atlas")

from config import (
    DRIVE_DB_PATH, CONFIG_DIR, PEXELS_API_KEY_PATH, PIXABAY_API_KEY_PATH,
    FOOTAGE_RESULTS_PER_QUERY
)
from director.api_key_manager import get_or_prompt_api_key
from collectors.pexels import PexelsCollector
from collectors.pixabay import PixabayCollector
from collectors.archive_org import ArchiveOrgCollector

pexels_key = get_or_prompt_api_key(PEXELS_API_KEY_PATH, "Pexels API key", "pexels.com/api")
pixabay_key = get_or_prompt_api_key(PIXABAY_API_KEY_PATH, "Pixabay API key", "pixabay.com/api/docs")

pexels = PexelsCollector(pexels_key)
pixabay = PixabayCollector(pixabay_key)
archive = ArchiveOrgCollector()

conn = sqlite3.connect(DRIVE_DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    keyword TEXT,
    identifier TEXT UNIQUE,
    filename TEXT,
    title TEXT,
    description TEXT,
    filesize_mb REAL,
    duration_seconds REAL,
    url TEXT,
    filepath TEXT,
    local_cache_path TEXT
)
""")
conn.commit()

cur.execute("PRAGMA table_info(assets)")
cols = [r[1] for r in cur.fetchall()]
if "local_cache_path" not in cols:
    cur.execute("ALTER TABLE assets ADD COLUMN local_cache_path TEXT")
    conn.commit()

# FIXED: Use absolute path for keywords.txt
keywords_path = os.path.join(os.path.dirname(__file__), "keywords.txt")
with open(keywords_path) as f:
    keywords = [l.strip() for l in f if l.strip()]

def insert_asset(source, keyword, resolved):
    identifier = resolved["identifier"]
    cur.execute("SELECT id FROM assets WHERE identifier=?", (identifier,))
    if cur.fetchone():
        return False
    cur.execute("""
        INSERT INTO assets(source, keyword, identifier, title, description,
                            duration_seconds, url, filepath, local_cache_path)
        VALUES (?,?,?,?,?,?,?,NULL,NULL)
    """, (source, keyword, identifier, resolved.get("title",""), "",
          resolved.get("duration"), resolved["url"]))
    return True

for keyword in keywords:
    print("\nSearching: " + keyword)
    total_inserted = 0

    try:
        for item in pexels.search(keyword, FOOTAGE_RESULTS_PER_QUERY):
            resolved = pexels.resolve(item)
            if resolved and insert_asset("pexels", keyword, resolved):
                total_inserted += 1
    except Exception as e:
        print("Pexels search failed: " + str(e))

    try:
        for item in pixabay.search(keyword, FOOTAGE_RESULTS_PER_QUERY):
            resolved = pixabay.resolve(item)
            if resolved and insert_asset("pixabay", keyword, resolved):
                total_inserted += 1
    except Exception as e:
        print("Pixabay search failed: " + str(e))

    if total_inserted == 0:
        print("No Pexels/Pixabay hits, falling back to Internet Archive for this keyword.")
        try:
            for item in archive.search(keyword, rows=FOOTAGE_RESULTS_PER_QUERY):
                identifier = item.get("identifier")
                if not identifier:
                    continue
                try:
                    files, server, dir_path = archive.get_files(identifier)
                except Exception:
                    continue
                files_with_size = [f for f in files if f.get("size")]
                if not files_with_size or not server:
                    continue
                chosen = sorted(files_with_size, key=lambda x: int(x["size"]))[0]
                url = "https://" + server + dir_path + "/" + chosen["name"]
                resolved = {
                    "url": url, "duration": None,
                    "title": item.get("title", ""),
                    "identifier": "archive_" + identifier,
                }
                if insert_asset("archive.org", keyword, resolved):
                    total_inserted += 1
        except Exception as e:
            print("Archive.org fallback failed: " + str(e))

    conn.commit()
    print("Inserted " + str(total_inserted) + " new assets for \'" + keyword + "\'")

conn.close()
print("\nDone. Module 1 is discovery-only now - no video files downloaded yet.")