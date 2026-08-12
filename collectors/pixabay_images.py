
import requests

SEARCH_URL = "https://pixabay.com/api/"


class PixabayImageCollector:
    def __init__(self, api_key):
        self.api_key = api_key

    def search(self, query, per_page=5):
        per_page = max(per_page, 3)
        r = requests.get(SEARCH_URL, params={"key": self.api_key, "q": query, "per_page": per_page})
        r.raise_for_status()
        return r.json().get("hits", [])

    def resolve(self, item):
        url = item.get("largeImageURL") or item.get("webformatURL")
        if not url:
            return None
        return {
            "url": url,
            "title": item.get("tags", "pixabay_image"),
            "identifier": "pixabay_img_" + str(item.get("id")),
        }
