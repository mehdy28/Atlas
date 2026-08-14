
import os
import sys
import json
import sqlite3
import requests

sys.path.append("/content/Atlas")

from config import (
    DRIVE_DB_PATH, PEXELS_API_KEY_PATH, PIXABAY_API_KEY_PATH,
    FOOTAGE_KEYWORDS_PATH, VIDEO_RESULTS_PER_KEYWORD_DEFAULT, IMAGE_RESULTS_PER_KEYWORD_DEFAULT,
    IMAGES_DIR, IMAGE_DISPLAY_DURATION
)
from director.api_key_manager import get_or_prompt_api_key
from collectors.pexels import PexelsCollector
from collectors.pixabay import PixabayCollector
from collectors.pexels_images import PexelsImageCollector
from collectors.pixabay_images import PixabayImageCollector


def ensure_schema(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT, keyword TEXT, identifier TEXT UNIQUE, filename TEXT,
        title TEXT, description TEXT, filesize_mb REAL, duration_seconds REAL,
        url TEXT, filepath TEXT, local_cache_path TEXT
    )
    """)
    for col, coltype in [("asset_type", "TEXT DEFAULT 'video'"), ("scenes_extracted", "INTEGER DEFAULT 0")]:
        cur.execute("PRAGMA table_info(assets)")
        if col not in [r[1] for r in cur.fetchall()]:
            cur.execute("ALTER TABLE assets ADD COLUMN " + col + " " + coltype)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scenes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER, scene_index INTEGER, start_seconds REAL, end_seconds REAL,
        duration_seconds REAL, thumbnail_path TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id)
    )
    """)
    for col, coltype in [("caption", "TEXT"), ("caption_status", "TEXT DEFAULT 'pending'"),
                          ("times_used", "INTEGER DEFAULT 0"), ("last_used_at", "TEXT")]:
        cur.execute("PRAGMA table_info(scenes)")
        if col not in [r[1] for r in cur.fetchall()]:
            cur.execute("ALTER TABLE scenes ADD COLUMN " + col + " " + coltype)


def insert_video_asset(cur, source, keyword, resolved):
    identifier = resolved["identifier"]
    cur.execute("SELECT id FROM assets WHERE identifier=?", (identifier,))
    if cur.fetchone():
        return False
    cur.execute("""
        INSERT INTO assets(source, keyword, identifier, title, description,
                            duration_seconds, url, filepath, asset_type, scenes_extracted)
        VALUES (?,?,?,?,?,?,?,NULL,'video',0)
    """, (source, keyword, identifier, resolved.get("title",""), "", resolved.get("duration"), resolved["url"]))
    return True


def insert_image_asset(cur, source, keyword, resolved, images_dir, image_duration):
    identifier = resolved["identifier"]
    cur.execute("SELECT id FROM assets WHERE identifier=?", (identifier,))
    if cur.fetchone():
        return False

    ext = os.path.splitext(resolved["url"].split("?")[0])[1] or ".jpg"
    local_path = os.path.join(images_dir, identifier + ext)

    if not os.path.exists(local_path):
        try:
            r = requests.get(resolved["url"], timeout=30)
            r.raise_for_status()
            with open(local_path, "wb") as out:
                out.write(r.content)
        except Exception:
            return False

    cur.execute("""
        INSERT INTO assets(source, keyword, identifier, title, description,
                            duration_seconds, url, filepath, asset_type, scenes_extracted)
        VALUES (?,?,?,?,?,?,?,?,'image',1)
    """, (source, keyword, identifier, resolved.get("title",""), "", image_duration, resolved["url"], local_path))
    asset_id = cur.lastrowid

    cur.execute("""
        INSERT INTO scenes(asset_id, scene_index, start_seconds, end_seconds, duration_seconds, thumbnail_path, caption_status)
        VALUES (?,0,0.0,?,?,?,'pending')
    """, (asset_id, image_duration, image_duration, local_path))
    return True


def discover_for_keywords(keywords, video_per_keyword, image_per_keyword,
                           pexels_key, pixabay_key):
    pexels_video = PexelsCollector(pexels_key)
    pixabay_video = PixabayCollector(pixabay_key)
    pexels_img = PexelsImageCollector(pexels_key)
    pixabay_img = PixabayImageCollector(pixabay_key)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    conn = sqlite3.connect(DRIVE_DB_PATH)
    cur = conn.cursor()
    ensure_schema(cur)
    conn.commit()

    video_total, image_total = 0, 0

    for keyword in keywords:
        print("\\nKeyword: " + keyword)
        v_count, i_count = 0, 0

        try:
            for item in pexels_video.search(keyword, video_per_keyword):
                resolved = pexels_video.resolve(item)
                if resolved and insert_video_asset(cur, "pexels", keyword, resolved):
                    v_count += 1
        except Exception as e:
            print("  Pexels video search failed: " + str(e))

        try:
            for item in pixabay_video.search(keyword, video_per_keyword):
                resolved = pixabay_video.resolve(item)
                if resolved and insert_video_asset(cur, "pixabay", keyword, resolved):
                    v_count += 1
        except Exception as e:
            print("  Pixabay video search failed: " + str(e))

        try:
            for item in pexels_img.search(keyword, image_per_keyword):
                resolved = pexels_img.resolve(item)
                if resolved and insert_image_asset(cur, "pexels", keyword, resolved, IMAGES_DIR, IMAGE_DISPLAY_DURATION):
                    i_count += 1
        except Exception as e:
            print("  Pexels image search failed: " + str(e))

        try:
            for item in pixabay_img.search(keyword, image_per_keyword):
                resolved = pixabay_img.resolve(item)
                if resolved and insert_image_asset(cur, "pixabay", keyword, resolved, IMAGES_DIR, IMAGE_DISPLAY_DURATION):
                    i_count += 1
        except Exception as e:
            print("  Pixabay image search failed: " + str(e))

        conn.commit()
        video_total += v_count
        image_total += i_count
        print("  New videos: " + str(v_count) + " | New images: " + str(i_count))

    conn.close()
    return video_total, image_total


if __name__ == "__main__":
    if not os.path.exists(FOOTAGE_KEYWORDS_PATH):
        raise SystemExit("No footage_keywords.json found. Run generate_script.py first.")

    with open(FOOTAGE_KEYWORDS_PATH) as f:
        keywords = json.load(f)

    if not keywords:
        raise SystemExit("footage_keywords.json is empty - nothing to search for.")

    print("Searching footage for " + str(len(keywords)) + " keywords (narrow default pass)...")

    pexels_key = get_or_prompt_api_key(PEXELS_API_KEY_PATH, "Pexels API key", "pexels.com/api")
    pixabay_key = get_or_prompt_api_key(PIXABAY_API_KEY_PATH, "Pixabay API key", "pixabay.com/api/docs")

    v_total, i_total = discover_for_keywords(
        keywords, VIDEO_RESULTS_PER_KEYWORD_DEFAULT, IMAGE_RESULTS_PER_KEYWORD_DEFAULT,
        pexels_key, pixabay_key
    )

    print("\\nTotal new videos: " + str(v_total) + " | Total new images: " + str(i_total))
    print("Done.")
