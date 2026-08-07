
import os
import requests


def _dir_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for fname in files:
            fp = os.path.join(root, fname)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total


def _evict_lru(cache_dir, max_bytes):
    entries = []
    for root, _, files in os.walk(cache_dir):
        for fname in files:
            fp = os.path.join(root, fname)
            entries.append((fp, os.path.getmtime(fp), os.path.getsize(fp)))
    entries.sort(key=lambda x: x[1])
    total = sum(e[2] for e in entries)
    i = 0
    while total > max_bytes and i < len(entries):
        fp, _, size = entries[i]
        try:
            os.remove(fp)
            total -= size
        except OSError:
            pass
        i += 1


def get_or_download(asset_id, source_url, cache_dir, max_cache_bytes, timeout=60):
    os.makedirs(cache_dir, exist_ok=True)
    ext = os.path.splitext(source_url.split("?")[0])[1] or ".mp4"
    local_path = os.path.join(cache_dir, "asset_" + str(asset_id) + ext)

    if os.path.exists(local_path):
        os.utime(local_path, None)
        return local_path

    resp = requests.get(source_url, stream=True, timeout=timeout)
    resp.raise_for_status()
    tmp_path = local_path + ".part"
    with open(tmp_path, "wb") as out:
        for chunk in resp.iter_content(1024 * 1024):
            out.write(chunk)
    os.replace(tmp_path, local_path)

    if _dir_size(cache_dir) > max_cache_bytes:
        _evict_lru(cache_dir, max_cache_bytes)

    return local_path
