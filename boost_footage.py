
import os
import sys
import json
import re

sys.path.append("/content/Atlas")

from config import (
    LOW_RELEVANCE_PARAGRAPHS_PATH, PEXELS_API_KEY_PATH, PIXABAY_API_KEY_PATH,
    BOOST_VIDEO_RESULTS_PER_KEYWORD, BOOST_IMAGE_RESULTS_PER_KEYWORD,
    GENERIC_CONCEPT_QUERIES, PARAGRAPH_QUERY_OVERRIDES_PATH, MAX_BOOST_PARAGRAPHS,
    LOW_RELEVANCE_THRESHOLD, MAX_CLIPS_PER_PARAGRAPH, SEARCH_CANDIDATES_PER_PARAGRAPH,
    MIN_CLIP_DURATION_SECONDS
)
from director.api_key_manager import get_or_prompt_api_key
from discover_footage import discover_for_keywords
from search.generic_fallback import find_best_query

STOPWORDS = {"the","a","an","is","are","was","were","to","of","in","on","for","and","or",
             "that","this","it","as","by","with","from","at","be","has","have","its","their"}


def extract_keyword_phrase(paragraph_text, max_words=4):
    words = re.findall(r"[A-Za-z]+", paragraph_text)
    significant = [w for w in words if w.lower() not in STOPWORDS and len(w) > 3]
    return " ".join(significant[:max_words]) if significant else paragraph_text[:40]


if not os.path.exists(LOW_RELEVANCE_PARAGRAPHS_PATH):
    print("No low_relevance_paragraphs.json found - nothing to boost.")
    raise SystemExit()

with open(LOW_RELEVANCE_PARAGRAPHS_PATH) as f:
    low_relevance = json.load(f)

if not low_relevance:
    print("No low-relevance paragraphs - skipping boost round entirely.")
    raise SystemExit()

print("Phase 1: trying existing footage with generic fallback queries (no downloads)...")

overrides = {}
still_weak = []

for p in low_relevance:
    best_query, best_avg, _ = find_best_query(
        p["text"], p["target_duration_seconds"], MIN_CLIP_DURATION_SECONDS,
        SEARCH_CANDIDATES_PER_PARAGRAPH, GENERIC_CONCEPT_QUERIES
    )
    if best_avg >= LOW_RELEVANCE_THRESHOLD:
        overrides[str(p["paragraph_index"])] = best_query
        print("  [p" + str(p["paragraph_index"]) + "] RESOLVED via existing footage - query: \"" + best_query + "\" (relevance " + str(round(best_avg,3)) + ")")
    else:
        still_weak.append(p)
        print("  [p" + str(p["paragraph_index"]) + "] still weak (best=" + str(round(best_avg,3)) + ") - queued for new discovery")

with open(PARAGRAPH_QUERY_OVERRIDES_PATH, "w") as f:
    json.dump(overrides, f, indent=2)

print("\\nPhase 1 resolved " + str(len(overrides)) + "/" + str(len(low_relevance)) + " paragraphs from existing footage - no new downloads needed for those.")

if not still_weak:
    print("All paragraphs resolved without any new discovery. Skipping Phase 2 entirely.")
    print("NEEDS_NEW_FOOTAGE=false")
    raise SystemExit()

still_weak = still_weak[:MAX_BOOST_PARAGRAPHS]
print("\\nPhase 2: targeted new discovery for " + str(len(still_weak)) + " paragraph(s) (capped at " + str(MAX_BOOST_PARAGRAPHS) + ")...")

boost_keywords = [extract_keyword_phrase(p["text"]) for p in still_weak]
boost_keywords = list(dict.fromkeys(boost_keywords))

for k in boost_keywords:
    print("  - " + k)

pexels_key = get_or_prompt_api_key(PEXELS_API_KEY_PATH, "Pexels API key", "pexels.com/api")
pixabay_key = get_or_prompt_api_key(PIXABAY_API_KEY_PATH, "Pixabay API key", "pixabay.com/api/docs")

v_total, i_total = discover_for_keywords(
    boost_keywords, BOOST_VIDEO_RESULTS_PER_KEYWORD, BOOST_IMAGE_RESULTS_PER_KEYWORD,
    pexels_key, pixabay_key
)

print("\\nBoost discovery complete. New videos: " + str(v_total) + " | New images: " + str(i_total))
print("NEEDS_NEW_FOOTAGE=true")
print("Done.")
