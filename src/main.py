from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

try:
    import yaml
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:
    missing_package = exc.name
    print(
        f"Missing dependency '{missing_package}'. "
        "Install dependencies with: pip install -r requirements.txt"
    )
    raise SystemExit(1) from exc

from src.dedupe import DEFAULT_SEEN_PATH, filter_new_jobs, load_seen_jobs, save_seen_jobs
from src.notifier_email import send_email_alert
from src.notifier_telegram import send_telegram_alert
from src.scoring import score_job
from src.sources import adzuna, arbeitnow, remotive


CONFIG_PATH = Path("config.yaml")
SourceFetcher = Callable[[dict[str, Any]], list[dict[str, Any]]]


SOURCES: dict[str, SourceFetcher] = {
    "remotive": remotive.fetch_jobs,
    "adzuna": adzuna.fetch_jobs,
    "arbeitnow": arbeitnow.fetch_jobs,
}


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def fetch_all_jobs(config: dict[str, Any]) -> list[dict[str, Any]]:
    enabled_sources = config.get("enabled_sources", {})
    all_jobs: list[dict[str, Any]] = []

    for source_name, fetcher in SOURCES.items():
        if not enabled_sources.get(source_name, False):
            continue

        try:
            jobs = fetcher(config)
        except Exception as exc:  # Keeps one unexpected source issue from stopping the run.
            print(f"{source_name.title()} source failed unexpectedly: {exc}")
            continue

        print(f"Fetched {len(jobs)} jobs from {source_name.title()}.")
        all_jobs.extend(jobs)

    return all_jobs


def unique_by_url(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for job in jobs:
        url = job.get("url")
        if url:
            unique[url] = job
    return list(unique.values())


def score_and_filter_jobs(jobs: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    minimum_score = int(config.get("minimum_score", 60))
    scored_jobs = [score_job(job, config) for job in jobs]
    matching_jobs = [job for job in scored_jobs if job["score"] >= minimum_score]
    return sorted(matching_jobs, key=lambda job: job["score"], reverse=True)


def format_alert(jobs: list[dict[str, Any]]) -> str:
    lines = ["New AI Ops Job Matches", ""]

    for index, job in enumerate(jobs, start=1):
        lines.extend(
            [
                f"{index}. {job.get('title', 'Untitled role')}",
                f"   Company: {job.get('company') or 'Unknown'}",
                f"   Location: {job.get('location') or 'Unknown'}",
                f"   Source: {job.get('source') or 'Unknown'}",
                f"   Score: {job.get('score', 0)}",
                f"   Why matched: {job.get('match_reason') or 'Keyword match'}",
                f"   Link: {job.get('url')}",
                "",
            ]
        )

    return "\n".join(lines).strip()


def send_alert(message: str, config: dict[str, Any]) -> None:
    notifications = config.get("notifications", {})
    sent = False

    if notifications.get("telegram", True):
        sent = send_telegram_alert(message) or sent
    if notifications.get("email", True):
        sent = send_email_alert(message) or sent

    if not sent:
        print(message)


def run(dry_run: bool) -> int:
    load_dotenv()
    config = load_config()

    jobs = unique_by_url(fetch_all_jobs(config))
    matching_jobs = score_and_filter_jobs(jobs, config)

    if dry_run:
        if not matching_jobs:
            print("No matching jobs found in dry-run.")
            return 0
        print(format_alert(matching_jobs))
        return 0

    seen_urls = load_seen_jobs(DEFAULT_SEEN_PATH)
    new_jobs = filter_new_jobs(matching_jobs, seen_urls)

    if not new_jobs:
        print("No new matching jobs.")
        return 0

    alert_message = format_alert(new_jobs)
    send_alert(alert_message, config)

    updated_seen_urls = seen_urls | {job["url"] for job in new_jobs if job.get("url")}
    save_seen_jobs(updated_seen_urls, DEFAULT_SEEN_PATH)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find and alert on AI operations job matches.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print matches without sending alerts.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
