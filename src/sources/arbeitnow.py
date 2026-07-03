from __future__ import annotations

from typing import Any

import requests


API_URL = "https://www.arbeitnow.com/api/job-board-api"


def _normalize(job: dict[str, Any]) -> dict[str, Any]:
    tags = job.get("tags") or []
    location = job.get("location") or ""
    text = f"{job.get('title', '')} {job.get('description', '')} {location} {' '.join(tags)}".lower()

    return {
        "title": job.get("title", ""),
        "company": job.get("company_name", ""),
        "location": location,
        "remote": bool(job.get("remote")) or "remote" in text,
        "source": "Arbeitnow",
        "url": job.get("url", ""),
        "description": job.get("description", ""),
        "posted_at": str(job.get("created_at", "")),
    }


def fetch_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    max_jobs = int(config.get("max_jobs_per_source", 50))

    try:
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        print(f"Arbeitnow source failed: {exc}")
        return []

    query_terms = [query.lower() for query in config.get("search_queries", [])]
    jobs: list[dict[str, Any]] = []

    for raw_job in data.get("data", []):
        job = _normalize(raw_job)
        searchable = f"{job['title']} {job['description']} {job['location']}".lower()
        likely_match = any(term in searchable for term in query_terms)
        likely_remote = job["remote"] or "remote" in searchable

        if likely_remote and likely_match:
            jobs.append(job)
        elif likely_remote:
            # Keep remote jobs for scoring because Arbeitnow has no search endpoint.
            jobs.append(job)

        if len(jobs) >= max_jobs:
            break

    return jobs
