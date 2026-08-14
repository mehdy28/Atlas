
import os
import sys
import json
import re

sys.path.append("/content/Atlas")

from config import (
    LOW_RELEVANCE_PARAGRAPHS_PATH, PEXELS_API_KEY_PATH, PIXABAY_API_KEY_PATH,
    BOOST_VIDEO_RESULTS_PER_KEYWORD, BOOST_IMAGE_RESULTS_PER_KEYWORD
)
from director.api_key_manager import get_or_prompt_api_key
from discover_footage import discover_for_keywords

STOPWORDS = {"the","a","an","is","are","was","were","to","of","in","on","for","and","or",
             "that","this","it","as","by","with","from","at","be","has","have","its","their"}


def extract_keyword_phrase(paragraph_text, max_words=4):
    """Pulls a short, concrete search phrase out of a weak paragraph's own text."""
    words = re.findall(r"[A-Za-z]+", paragraph_text)
    significant = [w for w in words if w.lower() not in STOPWORDS and len(w) > 3]
    return " ".join(significant[:max_words]) if significant else paragraph_text[:40]


if not os.path.exists(LOW_RELEVANCE_PARAGRAPHS_PATH):
    print("No low_relevance_paragraphs.json found - nothing to boost.")
    raise SystemExit()

with open(LOW_RELEVANCE_PARAGRAPHS_PATH) as f:
    low_relevance = json.load(f)

if not low_relevance:
    print("No low-relevance paragraphs - skipping boost round.")
    raise SystemExit()

boost_keywords = [extract_keyword_phrase(p["text"]) for p in low_relevance]
boost_keywords = list(dict.fromkeys(boost_keywords))  # de-dupe, preserve order

print("Boost round for " + str(len(boost_keywords)) + " targeted keyword(s):")
for k in boost_keywords:
    print("  - " + k)

pexels_key = get_or_prompt_api_key(PEXELS_API_KEY_PATH, "Pexels API key", "pexels.com/api")
pixabay_key = get_or_prompt_api_key(PIXABAY_API_KEY_PATH, "Pixabay API key", "pixabay.com/api/docs")

v_total, i_total = discover_for_keywords(
    boost_keywords, BOOST_VIDEO_RESULTS_PER_KEYWORD, BOOST_IMAGE_RESULTS_PER_KEYWORD,
    pexels_key, pixabay_key
)

print("\\nBoost round complete. New videos: " + str(v_total) + " | New images: " + str(i_total))
print("Done.")
