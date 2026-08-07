
import requests

SEARCH_URL = "https://pixabay.com/api/videos/"


class PixabayCollector:
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query, per_page=15):
        r = requests.get(SEARCH_URL, params={"key": self.api_key, "q": query, "per_page": per_page})
        r.raise_for_status()
        return r.json().get("hits", [])

    def resolve(self, item, preferred="medium"):
        videos = item.get("videos", {})
        chosen = videos.get(preferred) or videos.get("small") or videos.get("large") or videos.get("tiny")
        if not chosen or not chosen.get("url"):
            return None
        return {
            "url": chosen["url"],
            "width": chosen.get("width"),
            "height": chosen.get("height"),
            "duration": item.get("duration"),
            "title": item.get("tags", "pixabay_video"),
            "identifier": "pixabay_" + str(item.get("id")),
        }
