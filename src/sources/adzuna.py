from __future__ import annotations

import os
from typing import Any

import requests


def _normalize(job: dict[str, Any]) -> dict[str, Any]:
    location_data = job.get("location") or {}
    location_parts = location_data.get("area") or []
    location = " / ".join(location_parts) if location_parts else location_data.get("display_name", "")
    title = job.get("title", "")
    description = job.get("description", "")
    text = f"{title} {description} {location}".lower()

    return {
        "title": title,
        "company": (job.get("company") or {}).get("display_name", ""),
        "location": location,
        "remote": "remote" in text or "work from home" in text,
        "source": "Adzuna",
        "url": job.get("redirect_url", ""),
        "description": description,
        "posted_at": job.get("created", ""),
    }


def fetch_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        print("Adzuna credentials are missing; skipping Adzuna.")
        return []

    country = config.get("country", "au")
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    queries = config.get("search_queries", [])
    max_jobs = int(config.get("max_jobs_per_source", 50))
    jobs_by_url: dict[str, dict[str, Any]] = {}

    for query in queries:
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": query,
            "results_per_page": min(max_jobs, 50),
            "content-type": "application/json",
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            print(f"Adzuna source failed for '{query}': {exc}")
            continue

        for raw_job in data.get("results", []):
            job = _normalize(raw_job)
            if job["url"]:
                jobs_by_url[job["url"]] = job
            if len(jobs_by_url) >= max_jobs:
                return list(jobs_by_url.values())

    return list(jobs_by_url.values())
