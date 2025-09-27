# crispy-goggles

![CI](https://github.com/forever-efficient/crispy-goggles/actions/workflows/ci.yml/badge.svg)

Python Automation

## Quick setup

1. Create a virtual environment and install the project (editable):

```bash
make setup
```

2. Install Playwright browsers (only needed once):

```bash
make install-browsers
```

That's it — you can run unit tests with `pytest` and Behave scenarios with `behave`.

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
make setup
playwright install
```

- Common fixes:
  - Missing system libraries on Linux runners: use `playwright install --with-deps` (CI uses this).
  - Headless vs headed differences: try running with `context.browser = context.playwright.chromium.launch(headless=False)` locally to debug UI issues.

## FAQ

- Why was `requirements.txt` removed?

  We moved dependency declarations into `pyproject.toml` and use an editable install (`pip install -e '.[dev]'`) for development and CI. This keeps packaging and CI aligned and avoids duplication. Use `make setup` to create the venv and install dependencies.

## Local-only tests and CI

- Tests/scenarios tagged with `@local` are intended to run only on a developer machine. CI explicitly skips these scenarios to avoid launching local browsers or depending on desktop-only resources.

- CI behavior:
  - The GitHub Actions workflow runs Behave with the tag exclusion `-t ~@local`, so scenarios tagged `@local` are skipped. The workflow also prints which files contain `@local` tags for visibility.

- How to run local-only scenarios locally (Chrome):

```bash
# create and activate venv (if you haven't already)
make setup
source .venv/bin/activate

# run only local scenarios (those tagged @local)
USE_CHROME=1 ./.venv/bin/python -m behave -f pretty -t @local

# run all non-local scenarios (what CI runs)
USE_CHROME=1 ./.venv/bin/python -m behave -f pretty -t ~@local
```

- Useful environment variables:
  - `CHROME_HEADLESS=1` — run Chrome in headless mode for faster CI-like runs locally
  - `CHROME_USER_AGENT` — override the browser user-agent string
  - `TEST_LOGIN_USERNAME`, `TEST_LOGIN_PASSWORD` — override the credentials used by the local login scenario

Note: The `@local` tag is a convention used to signal tests that require a human-like browser environment or local resources; CI will ignore them.
