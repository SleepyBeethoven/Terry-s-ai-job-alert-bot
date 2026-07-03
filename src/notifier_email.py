from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


REQUIRED_ENV = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "ALERT_EMAIL_TO"]


def is_configured() -> bool:
    return all(os.getenv(name) for name in REQUIRED_ENV)


def send_email_alert(message: str) -> bool:
    """Send an email alert. Returns True if sent, False if not configured or failed."""
    if not is_configured():
        print("Email settings are missing; skipping email.")
        return False

    smtp_host = os.environ["SMTP_HOST"]
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ["SMTP_USER"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    alert_to = os.environ["ALERT_EMAIL_TO"]

    email = EmailMessage()
    email["Subject"] = "New AI Ops Job Matches"
    email["From"] = smtp_user
    email["To"] = alert_to
    email.set_content(message)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(email)
    except (OSError, smtplib.SMTPException) as exc:
        print(f"Email alert failed: {exc}")
        return False

    return True
