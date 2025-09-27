# crispy-goggles

![CI](https://github.com/forever-efficient/crispy-goggles/actions/workflows/ci.yml/badge.svg)

Python Automation

## CI and Playwright setup

This repository uses GitHub Actions to run unit tests and Playwright/Behave browser tests. A scheduled workflow refreshes Playwright browsers daily and can send failure notifications.

Required repository secrets for email notifications:
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFY_EMAIL`

To enable Slack notifications, add a `SLACK_WEBHOOK` secret and uncomment the Slack step in `.github/workflows/refresh-browsers.yml`.

## Adding repository secrets (GitHub)

1. Go to the repository on GitHub.
2. Click Settings -> Secrets and variables -> Actions -> New repository secret.
3. Add the secret name (for example `SMTP_HOST`) and its value, then click "Add secret".
4. Repeat for each required secret: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFY_EMAIL`, and optionally `SLACK_WEBHOOK`.

Once secrets are added, you can re-enable the notification steps in `.github/workflows/refresh-browsers.yml` by uncommenting the corresponding blocks.

## Playwright troubleshooting (quick)

- If Playwright tests fail in CI with browser errors, try running locally and installing browsers:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

- Common fixes:
  - Missing system libraries on Linux runners: use `playwright install --with-deps` (CI uses this).
  - Headless vs headed differences: try running with `context.browser = context.playwright.chromium.launch(headless=False)` locally to debug UI issues.
