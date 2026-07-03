from __future__ import annotations

import json
from pathlib import Path


DEFAULT_SEEN_PATH = Path("seen_jobs.json")


def load_seen_jobs(path: Path = DEFAULT_SEEN_PATH) -> set[str]:
    """Load previously seen job URLs, recovering from missing or invalid files."""
    if not path.exists():
        return set()

    try:
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            return set()
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return set()

    if isinstance(data, list):
        return {str(url) for url in data if url}
    if isinstance(data, dict):
        urls = data.get("seen_urls", [])
        if isinstance(urls, list):
            return {str(url) for url in urls if url}
    return set()


def filter_new_jobs(jobs: list[dict], seen_urls: set[str]) -> list[dict]:
    """Return jobs whose URLs are not already in the seen set."""
    return [job for job in jobs if job.get("url") and job["url"] not in seen_urls]


def save_seen_jobs(urls: set[str], path: Path = DEFAULT_SEEN_PATH) -> None:
    """Persist seen URLs in a stable, readable format."""
    path.write_text(
        json.dumps({"seen_urls": sorted(urls)}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
