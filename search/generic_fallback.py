
from search.query import search


def find_best_query(paragraph_text, target_duration, min_clip_duration, candidates_to_fetch, generic_queries):
    """
    Tries the paragraph's own text plus a curated list of generic
    documentary B-roll concepts against the EXISTING search index (no
    downloads). Returns (best_query, avg_relevance, candidates) for
    whichever query scores highest - often a generic query beats a
    literal search on abstract/argumentative sentences.
    """
    candidates_list = [paragraph_text] + generic_queries
    best_query = paragraph_text
    best_avg = -1.0
    best_candidates = []

    for query in candidates_list:
        try:
            results = search(query, top_k=candidates_to_fetch, mark_used=False)
        except Exception:
            continue
        usable = [r for r in results if r["duration_seconds"] >= min_clip_duration]
        if not usable:
            continue
        avg = sum(r["relevance"] for r in usable[:4]) / len(usable[:4])
        if avg > best_avg:
            best_avg = avg
            best_query = query
            best_candidates = usable

    return best_query, max(best_avg, 0.0), best_candidates
