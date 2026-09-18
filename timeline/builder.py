
from search.query import search
from config import STRICT_CLIP_RELEVANCE_MIN


def fill_paragraph_with_clips(paragraph_text, target_duration, max_clips, candidates_to_fetch, min_clip_duration):
    """
    Runs a semantic search for the paragraph text, then greedily selects
    clips (best-scoring first) until their combined duration covers the
    target duration - BUT any candidate scoring below
    STRICT_CLIP_RELEVANCE_MIN is rejected outright, never selected, no
    matter how much time remains uncovered. This intentionally allows a
    paragraph to end up under-covered rather than filled with unrelated
    footage; the uncovered gap becomes an explicit signal for the
    image-generation fallback to handle.
    """
    candidates = search(paragraph_text, top_k=candidates_to_fetch, mark_used=False)

    selected = []
    rejected_low_relevance = []
    time_covered = 0.0

    for candidate in candidates:
        if len(selected) >= max_clips:
            break
        if time_covered >= target_duration:
            break

        if candidate["relevance"] < STRICT_CLIP_RELEVANCE_MIN:
            rejected_low_relevance.append(candidate)
            continue

        clip_duration = candidate["duration_seconds"]
        if clip_duration < min_clip_duration:
            continue

        remaining = target_duration - time_covered
        use_duration = min(clip_duration, remaining)

        if use_duration < min_clip_duration and selected:
            continue

        selected.append({
            "scene_id": candidate["scene_id"],
            "video_path": candidate["video_path"],
            "source_url": candidate.get("source_url"),
            "asset_type": candidate.get("asset_type", "video"),
            "caption": candidate["caption"],
            "relevance": candidate["relevance"],
            "source_start_seconds": candidate["start_seconds"],
            "source_end_seconds": candidate["start_seconds"] + use_duration,
            "use_duration_seconds": round(use_duration, 2),
        })
        time_covered += use_duration

    # No fallback-to-best-bad-match here anymore. If selected is empty or
    # time_covered < target_duration, that gap is real and gets reported
    # to the caller rather than silently papered over with a weak clip.
    uncovered_seconds = round(max(0.0, target_duration - time_covered), 2)

    from search.query import _load_index
    import sqlite3
    from datetime import datetime, timezone
    from config import DRIVE_DB_PATH

    if selected:
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

    return selected, time_covered, uncovered_seconds
