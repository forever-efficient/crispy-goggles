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

That's it — you can run unit tests with `pytest`. Browser tests now use Playwright via `pytest-playwright`.

## CI and Playwright setup

This repository uses GitHub Actions to run unit tests and Playwright-based browser tests. A scheduled workflow refreshes Playwright browsers daily and can send failure notifications.

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

- Tests marked with `@pytest.mark.local` are intended to run only on a developer machine. CI explicitly skips these tests to avoid launching local browsers or depending on desktop-only resources.

- CI behavior:
  - The GitHub Actions workflow runs pytest with the marker exclusion `-m "not local"`, so tests marked `local` are skipped. The workflow prints any local tests for visibility.

- How to run local-only tests locally:

```bash
# create and activate venv (if you haven't already)
make setup
source .venv/bin/activate

# run only local tests (those marked with pytest.mark.local)
. .venv/bin/activate
.venv/bin/python -m pytest -q -m local

# run all non-local tests (what CI runs)
. .venv/bin/activate
.venv/bin/python -m pytest -q -m "not local"
```

- Useful environment variables:
  - `PLAYWRIGHT_HEADLESS=1` — run Playwright in headless mode for faster CI-like runs locally
  - `TEST_LOGIN_USERNAME`, `TEST_LOGIN_PASSWORD` — override the credentials used by the local login test

Note: The `local` marker denotes tests that require a real desktop-like browser environment; CI will ignore them.

## Interactive auth-state helper (local-only)

The project includes a small interactive helper to capture Playwright storage state
(cookies + localStorage) and save it as `auth_state.json`. This file allows you to
reuse a logged-in session for local debugging without automating repeated logins.

Important safety notes:
- Do NOT commit `auth_state.json` to version control. The file is added to
  `.gitignore` by default.
- The helper and saved auth state are intended for local development only. The
  login test is explicitly skipped in CI and the test suite will not attempt to
  create or use `auth_state.json` inside CI.

How to create an auth state interactively:

1. Activate the project's virtualenv:

```bash
source .venv/bin/activate
```

2. Run the helper and sign in manually in the opened browser. When finished,
   return to the terminal and press ENTER to save the file:

```bash
.venv/bin/python scripts/ensure_auth_state.py --output auth_state.json --url https://x.com/login
```

3. Confirm `auth_state.json` was written and keep it local (do not commit).

How tests use the auth state:
- Set `TEST_USE_AUTH_STATE=1` when running tests locally to force tests to use
  `auth_state.json` (the `require_auth_state` fixture will try to launch the
  interactive helper locally if the file is missing, but will fail fast in CI).

Example local run using the recorded auth state:

```bash
export TEST_USE_AUTH_STATE=1
export TEST_LOGIN_USERNAME=you@example.com
.venv/bin/python -m pytest -q -m local
```

If `auth_state.json` is missing when you run the test locally with
`TEST_USE_AUTH_STATE=1`, the test harness will launch the interactive helper so
you can sign in and save the state.

If you'd like, we can add an optional README section showing how to safely add
the base64-encoded state into a private CI secret (but per project policy this
repo will not use auth state in CI by default).
