from __future__ import annotations

from typing import Any

import requests


API_URL = "https://remotive.com/api/remote-jobs"


def _normalize(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": job.get("candidate_required_location") or "Remote",
        "remote": True,
        "source": "Remotive",
        "url": job.get("url", ""),
        "description": job.get("description", ""),
        "posted_at": job.get("publication_date", ""),
    }


def fetch_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    jobs_by_url: dict[str, dict[str, Any]] = {}
    queries = config.get("search_queries", [])
    max_jobs = int(config.get("max_jobs_per_source", 50))

    for query in queries:
        try:
            response = requests.get(API_URL, params={"search": query}, timeout=20)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            print(f"Remotive source failed for '{query}': {exc}")
            continue

        for raw_job in data.get("jobs", []):
            job = _normalize(raw_job)
            if job["url"]:
                jobs_by_url[job["url"]] = job
            if len(jobs_by_url) >= max_jobs:
                return list(jobs_by_url.values())

    return list(jobs_by_url.values())
