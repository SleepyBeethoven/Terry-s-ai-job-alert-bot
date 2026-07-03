from __future__ import annotations

import re
from typing import Any


def _clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip().lower()


def _keyword_hits(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def score_job(job: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Score a normalized job from 0 to 100 and explain why it matched."""
    title = _clean_text(job.get("title"))
    description = _clean_text(job.get("description"))
    location = _clean_text(job.get("location"))
    combined = f"{title} {description} {location}"

    positive_keywords = config.get("positive_keywords", [])
    negative_keywords = config.get("negative_keywords", [])
    title_bonus_keywords = config.get("title_bonus_keywords", [])
    description_bonus_keywords = config.get("description_bonus_keywords", [])

    positive_hits = _keyword_hits(combined, positive_keywords)
    negative_hits = _keyword_hits(combined, negative_keywords)
    title_hits = _keyword_hits(title, title_bonus_keywords)
    description_hits = _keyword_hits(description, description_bonus_keywords)

    score = 10
    score += min(len(positive_hits) * 8, 48)
    score += min(len(title_hits) * 8, 32)
    score += min(len(description_hits) * 5, 25)

    if job.get("remote"):
        score += 8
    if "australia" in location or "au" == location or "remote" in location:
        score += 4

    score -= min(len(negative_hits) * 15, 60)

    # Strongly discourage roles that are likely outside the user's target profile.
    heavy_negative_hits = _keyword_hits(
        combined,
        ["software engineer", "research scientist", "data scientist", "pytorch", "tensorflow", "phd"],
    )
    if heavy_negative_hits:
        score -= 20

    score = max(0, min(100, score))

    reason_parts = []
    for hit in title_hits + description_hits + positive_hits:
        if hit not in reason_parts:
            reason_parts.append(hit)

    if negative_hits and score < 60:
        reason_parts.append(f"penalized for {', '.join(negative_hits[:3])}")

    reason = " + ".join(reason_parts[:6]) if reason_parts else "general AI operations keyword match"

    return {
        **job,
        "score": score,
        "match_reason": reason,
    }
