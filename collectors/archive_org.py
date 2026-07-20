
import requests
from collectors.base import BaseCollector

SEARCH_URL = "https://archive.org/advancedsearch.php"
METADATA_URL = "https://archive.org/metadata/{identifier}"


def _parse_duration(length_value):
    """
    IA file 'length' field is inconsistent: sometimes plain seconds
    ("754.32"), sometimes "HH:MM:SS" or "MM:SS". Normalize to seconds.
    Returns None if unparseable.
    """
    if not length_value:
        return None

    length_value = str(length_value).strip()

    try:
        return float(length_value)
    except ValueError:
        pass

    parts = length_value.split(":")
    try:
        parts = [float(p) for p in parts]
    except ValueError:
        return None

    if len(parts) == 3:
        h, m, s = parts
        return h * 3600 + m * 60 + s
    elif len(parts) == 2:
        m, s = parts
        return m * 60 + s

    return None


class ArchiveOrgCollector(BaseCollector):
    """Collector for the Internet Archive. No API key required."""

    def search(self, query, rows=20):
        params = {
            "q": f"({query}) AND mediatype:(movies)",
            "fl[]": ["identifier", "title", "description"],
            "rows": rows,
            "page": 1,
            "output": "json",
        }
        r = requests.get(SEARCH_URL, params=params)
        r.raise_for_status()
        return r.json().get("response", {}).get("docs", [])

    def get_files(self, identifier):
        r = requests.get(METADATA_URL.format(identifier=identifier))
        r.raise_for_status()
        data = r.json()
        files = [f for f in data.get("files", []) if f.get("name", "").lower().endswith(".mp4")]
        return files, data.get("server"), data.get("dir")

    def resolve_download(self, item, max_filesize_mb=80, max_duration_seconds=600):
        identifier = item.get("identifier")
        if not identifier:
            return None

        files, server, dir_path = self.get_files(identifier)
        files_with_size = [f for f in files if f.get("size")]
        if not files_with_size or not server:
            return None

        chosen = sorted(files_with_size, key=lambda x: int(x["size"]))[0]

        filesize_mb = int(chosen["size"]) / (1024 * 1024)
        if filesize_mb > max_filesize_mb:
            return None

        duration_seconds = _parse_duration(chosen.get("length"))
        if duration_seconds is not None and duration_seconds > max_duration_seconds:
            return None

        filename = f"{identifier}_{chosen['name']}".replace("/", "_")
        url = f"https://{server}{dir_path}/{chosen['name']}"
        return url, filename, round(filesize_mb, 2), duration_seconds
