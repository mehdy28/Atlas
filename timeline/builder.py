
from search.query import search


def fill_paragraph_with_clips(paragraph_text, target_duration, max_clips, candidates_to_fetch, min_clip_duration):
    """
    Runs a semantic search for the paragraph text, then greedily selects
    clips (best-scoring first) until their combined duration covers the
    target duration. The final clip is trimmed so total time matches
    target_duration exactly (never runs long, never leaves a gap).
    Marks each selected scene as used so future paragraphs naturally
    rotate to different footage.
    """
    candidates = search(paragraph_text, top_k=candidates_to_fetch, mark_used=False)

    selected = []
    time_covered = 0.0

    for candidate in candidates:
        if len(selected) >= max_clips:
            break
        if time_covered >= target_duration:
            break

        clip_duration = candidate["duration_seconds"]
        if clip_duration < min_clip_duration:
            continue

        remaining = target_duration - time_covered
        use_duration = min(clip_duration, remaining)

        if use_duration < min_clip_duration and selected:
            # Too small a sliver to be worth a cut; let the previous clip run long instead
            continue

        selected.append({
            "scene_id": candidate["scene_id"],
            "video_path": candidate["video_path"],
            "caption": candidate["caption"],
            "relevance": candidate["relevance"],
            "source_start_seconds": candidate["start_seconds"],
            "source_end_seconds": candidate["start_seconds"] + use_duration,
            "use_duration_seconds": round(use_duration, 2),
        })
        time_covered += use_duration

    if not selected and candidates:
        # Fallback: nothing met the duration threshold, just take the best match as-is
        best = candidates[0]
        selected.append({
            "scene_id": best["scene_id"],
            "video_path": best["video_path"],
            "caption": best["caption"],
            "relevance": best["relevance"],
            "source_start_seconds": best["start_seconds"],
            "source_end_seconds": best["end_seconds"],
            "use_duration_seconds": best["duration_seconds"],
        })

    # Now actually mark usage, only for clips we committed to
    from search.query import _load_index  # ensures index/module already warm
    import sqlite3
    from datetime import datetime, timezone
    from config import DRIVE_DB_PATH

    conn = sqlite3.connect(DRIVE_DB_PATH)
    cur = conn.cursor()
    now_str = datetime.now(timezone.utc).isoformat()
    for clip in selected:
        cur.execute(
            "UPDATE scenes SET times_used = times_used + 1, last_used_at = ? WHERE id = ?",
            (now_str, clip["scene_id"])
        )
    conn.commit()
    conn.close()

    return selected, time_covered
