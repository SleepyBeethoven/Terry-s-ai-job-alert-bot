from __future__ import annotations

import os

import requests


def is_configured() -> bool:
    return bool(os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"))


def send_telegram_alert(message: str) -> bool:
    """Send a Telegram alert. Returns True if sent, False if not configured or failed."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("Telegram settings are missing; skipping Telegram.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "disable_web_page_preview": True},
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Telegram alert failed: {exc}")
        return False

    return True
