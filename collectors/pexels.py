
import requests

SEARCH_URL = "https://api.pexels.com/videos/search"


class PexelsCollector:
    def __init__(self, api_key):
        self.headers = {"Authorization": api_key}

    def search(self, query, per_page=15):
        r = requests.get(SEARCH_URL, headers=self.headers, params={"query": query, "per_page": per_page})
        r.raise_for_status()
        return r.json().get("videos", [])

    def resolve(self, item, max_width=1920):
        files = item.get("video_files", [])
        if not files:
            return None
        good = [f for f in files if f.get("width") and f["width"] <= max_width]
        chosen = max(good, key=lambda f: f["width"]) if good else min(files, key=lambda f: f.get("width", 99999))
        return {
            "url": chosen["link"],
            "width": chosen.get("width"),
            "height": chosen.get("height"),
            "duration": item.get("duration"),
            "title": (item.get("user") or {}).get("name", "pexels_video"),
            "identifier": "pexels_" + str(item.get("id")),
        }
