
import sqlite3
import numpy as np
import faiss
from datetime import datetime, timezone

from config import (
    DRIVE_DB_PATH, FAISS_INDEX_PATH, FAISS_IDS_PATH,
    RELEVANCE_WEIGHT, USAGE_PENALTY_WEIGHT, RECENCY_PENALTY_WEIGHT
)
from search.embedder import embed_texts

_index = None
_scene_ids = None


def _load_index():
    global _index, _scene_ids
    if _index is None:
        _index = faiss.read_index(FAISS_INDEX_PATH)
        _scene_ids = np.load(FAISS_IDS_PATH)
    return _index, _scene_ids


def _score_candidates(candidates, now):
    scored = []
    for c in candidates:
        score = RELEVANCE_WEIGHT * c["relevance"]
        score -= USAGE_PENALTY_WEIGHT * c["times_used"]

        if c["last_used_at"]:
            try:
                last_used = datetime.fromisoformat(c["last_used_at"])
                hours_since = (now - last_used).total_seconds() / 3600.0
                if hours_since < 24:
                    recency_factor = max(0.0, 1.0 - (hours_since / 24.0))
                    score -= RECENCY_PENALTY_WEIGHT * recency_factor
            except Exception:
                pass

        c["score"] = score
        scored.append(c)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def search(query_text, top_k=10, mark_used=False):
    index, scene_ids = _load_index()

    query_embedding = embed_texts([query_text], batch_size=1)
    similarities, positions = index.search(query_embedding.astype(np.float32), top_k * 3)

    similarities = similarities[0]
    positions = positions[0]

    matched_ids = [int(scene_ids[p]) for p in positions if p != -1]

    if not matched_ids:
        return []

    conn = sqlite3.connect(DRIVE_DB_PATH)
    cur = conn.cursor()

    placeholders = ",".join("?" * len(matched_ids))
    cur.execute(f"""
        SELECT scenes.id, scenes.asset_id, scenes.caption, scenes.start_seconds,
               scenes.end_seconds, scenes.duration_seconds, scenes.thumbnail_path,
               scenes.times_used, scenes.last_used_at, assets.filepath, assets.keyword,
               assets.url, assets.asset_type
        FROM scenes
        JOIN assets ON scenes.asset_id = assets.id
        WHERE scenes.id IN ({placeholders})
    """, matched_ids)
    rows = cur.fetchall()
    row_by_id = {r[0]: r for r in rows}

    candidates = []
    for sim, scene_id in zip(similarities, matched_ids):
        row = row_by_id.get(scene_id)
        if not row:
            continue
        (_, asset_id, caption, start, end, duration, thumb_path,
         times_used, last_used_at, video_path, keyword, source_url, asset_type) = row

        candidates.append({
            "scene_id": scene_id,
            "asset_id": asset_id,
            "caption": caption,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": duration,
            "thumbnail_path": thumb_path,
            "video_path": video_path,
            "source_url": source_url,
            "asset_type": asset_type or "video",
            "keyword": keyword,
            "relevance": float(sim),
            "times_used": times_used or 0,
            "last_used_at": last_used_at,
        })

    now = datetime.now(timezone.utc)
    ranked = _score_candidates(candidates, now)
    top_results = ranked[:top_k]

    if mark_used:
        now_str = now.isoformat()
        for r in top_results:
            cur.execute(
                "UPDATE scenes SET times_used = times_used + 1, last_used_at = ? WHERE id = ?",
                (now_str, r["scene_id"])
            )
        conn.commit()

    conn.close()
    return top_results
