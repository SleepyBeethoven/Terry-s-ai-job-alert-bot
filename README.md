# AI Job Alert Bot

This bot searches public job APIs once per day and alerts you about roles that look like a good fit for AI operations, AI data operations, model evaluation, trust and safety, human-in-the-loop AI, data annotation coordination, and related project or team lead work.

It is designed for a bilingual Mandarin/English AI evaluation contractor profile with reviewer, moderator, project coordination, Salesforce/marketing operations, and AI data platform experience. It intentionally prioritizes operations, quality, coordination, and lead roles over pure machine learning engineering roles.

## What It Uses

- Remotive public API
- Adzuna API
- Arbeitnow public API
- `seen_jobs.json` to avoid sending the same job twice
- Optional Telegram alerts
- Optional email alerts
- GitHub Actions for daily scheduled runs

The bot does not scrape LinkedIn, Indeed, or sites that block scraping.

## Install Locally

Use Python 3.11, then install dependencies:

```bash
pip install -r requirements.txt
```

## Create Your `.env`

Copy the example file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and add the services you want to use.

## Get An Adzuna API Key

1. Go to [Adzuna Developer](https://developer.adzuna.com/).
2. Create a free developer account.
3. Create an application.
4. Copy your App ID and App Key into `.env`:

```env
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key
```

Adzuna is optional. If the keys are missing, the bot skips Adzuna gracefully.

## Test Locally

Dry-run mode fetches and scores jobs, prints matching jobs, and does not send alerts or update `seen_jobs.json`.

```bash
python -m src.main --dry-run
```

## Run A Real Alert

```bash
python -m src.main
```

In real mode, the bot:

1. Fetches jobs from enabled sources.
2. Scores each job.
3. Keeps jobs with a score of at least the configured minimum.
4. Removes jobs already stored in `seen_jobs.json`.
5. Sends Telegram and/or email alerts if configured.
6. Prints the alert to the console if no notification service is configured.
7. Updates `seen_jobs.json`.

If there are no new jobs, it prints:

```text
No new matching jobs.
```

## Telegram Alerts

1. Message [BotFather](https://t.me/BotFather) on Telegram.
2. Create a bot and copy the bot token.
3. Get your chat ID. One simple way is to message your bot, then visit:

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

4. Add these values to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

If either Telegram value is missing, Telegram is skipped.

## Email Alerts

Add SMTP settings to `.env`:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_password_or_app_password
ALERT_EMAIL_TO=recipient@example.com
```

For Gmail, you usually need an app password rather than your normal account password.

If any required email value is missing, email is skipped.

## GitHub Actions Setup

The workflow file is at `.github/workflows/job-alert.yml`.

It runs daily at `23:00 UTC`, which is around Sydney morning during AEST, and it can also be run manually.

Add these repository secrets in GitHub:

- `ADZUNA_APP_ID`
- `ADZUNA_APP_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `ALERT_EMAIL_TO`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Only add the secrets for services you plan to use. Adzuna, Telegram, and email are all optional.

To add secrets:

1. Open your GitHub repository.
2. Go to **Settings**.
3. Go to **Secrets and variables**.
4. Choose **Actions**.
5. Add each secret.

## Manually Run The GitHub Action

1. Open the repository on GitHub.
2. Click **Actions**.
3. Select **Daily AI Job Alert**.
4. Click **Run workflow**.

The workflow commits `seen_jobs.json` back to the repository after a successful run when there are new seen jobs to save.

## Change Keywords And Scoring

Edit `config.yaml`.

Useful sections:

- `search_queries`: controls what each source searches for.
- `minimum_score`: controls how selective the bot is.
- `positive_keywords`: terms that increase the score.
- `negative_keywords`: terms that reduce the score.
- `title_bonus_keywords`: title terms that get extra priority.
- `description_bonus_keywords`: profile-fit description terms.
- `max_jobs_per_source`: keeps API calls and alert size manageable.

## Limitations Of V1

- Job APIs may return noisy results.
- Adzuna requires API credentials.
- Some sources do not expose perfect remote filters, so the bot does best-effort filtering.
- `seen_jobs.json` is simple file-based persistence, which is fine for a small MVP but not ideal for multiple parallel runs.
- Scoring is keyword-based rather than using an LLM or embeddings.
- The bot only checks the sources configured in `config.yaml`.

## Future Improvements

- Add more public job APIs.
- Add richer location preferences.
- Add a small web dashboard.
- Add LLM-based fit summaries.
- Store jobs in SQLite.
- Add tests with mocked API responses.
- Add weekly summary reports.
