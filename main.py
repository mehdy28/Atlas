
import os
import sys
import sqlite3
import requests
from pathlib import Path

sys.path.append("/content/Atlas")

from config import VIDEO_DIR, DB_PATH, IA_RESULTS_PER_QUERY, IA_MAX_FILESIZE_MB
from collectors.archive_org import ArchiveOrgCollector

Path(VIDEO_DIR).mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    keyword TEXT,
    identifier TEXT,
    filename TEXT UNIQUE,
    title TEXT,
    description TEXT,
    filesize_mb REAL,
    url TEXT,
    filepath TEXT
)
""")
conn.commit()

collector = ArchiveOrgCollector()

with open("/content/Atlas/keywords.txt") as f:
    keywords = [line.strip() for line in f if line.strip()]

for keyword in keywords:
    print(f"\nSearching: {keyword}")
    try:
        results = collector.search(keyword, rows=IA_RESULTS_PER_QUERY)
    except Exception as e:
        print(f"Search failed for {keyword}: {e}")
        continue

    print(f"Found {len(results)} archive items")

    for item in results:
        try:
            resolved = collector.resolve_download(item, max_filesize_mb=IA_MAX_FILESIZE_MB)
        except Exception as e:
            print(f"Metadata failed for {item.get('identifier')}: {e}")
            continue

        if not resolved:
            continue

        url, filename, filesize_mb = resolved

        cur.execute("SELECT id FROM assets WHERE filename=?", (filename,))
        if cur.fetchone():
            continue

        filepath = os.path.join(VIDEO_DIR, filename)

        try:
            resp = requests.get(url, stream=True, timeout=30)
            resp.raise_for_status()
            with open(filepath, "wb") as out:
                for chunk in resp.iter_content(1024 * 1024):
                    out.write(chunk)

            cur.execute("""
                INSERT INTO assets(source, keyword, identifier, filename, title,
                                    description, filesize_mb, url, filepath)
                VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                "archive.org", keyword, item.get("identifier"), filename,
                item.get("title", ""), item.get("description", ""),
                filesize_mb, url, filepath
            ))
            conn.commit()
            print(f"Saved {filename} ({filesize_mb:.1f} MB)")

        except Exception as e:
            print(f"Failed {filename}: {e}")

conn.close()
print("\nDone.")
