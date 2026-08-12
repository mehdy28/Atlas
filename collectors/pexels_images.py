
import requests

SEARCH_URL = "https://api.pexels.com/v1/search"


class PexelsImageCollector:
    def __init__(self, api_key):
        self.headers = {"Authorization": api_key}

    def search(self, query, per_page=5):
        r = requests.get(SEARCH_URL, headers=self.headers, params={"query": query, "per_page": per_page})
        r.raise_for_status()
        return r.json().get("photos", [])

    def resolve(self, item):
        src = item.get("src", {})
        url = src.get("large2x") or src.get("large") or src.get("original")
        if not url:
            return None
        return {
            "url": url,
            "title": item.get("photographer", "pexels_image"),
            "identifier": "pexels_img_" + str(item.get("id")),
        }
