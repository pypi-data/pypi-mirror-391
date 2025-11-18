# pure_scraper/cache.py
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)

def _url_to_filename(url: str) -> Path:
    hash_name = hashlib.md5(url.encode()).hexdigest()
    return CACHE_DIR / f"{hash_name}.html"

def load_from_cache(url: str, max_age_hours: int = 24):
    file_path = _url_to_filename(url)
    if not file_path.exists():
        return None
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    if datetime.now() - mtime > timedelta(hours=max_age_hours):
        return None
    try:
        return file_path.read_text(encoding="utf-8")
    except Exception:
        return None

def save_to_cache(url: str, html: str):
    file_path = _url_to_filename(url)
    file_path.write_text(html, encoding="utf-8")
