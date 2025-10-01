# crispy-goggles


## Quick start

1. Create a virtual environment and install the project (dev extras):

```bash
make setup-dev
```

Activate the venv when you're ready to run tests:

```bash
source .venv/bin/activate
```

## Local browser tests (Playwright)

Playwright-based, browser-driven tests are local-only and are marked with
`@pytest.mark.local`. CI excludes those tests (`pytest -m "not local"`).

Run only local tests (interactive/headed):

```bash
.venv/bin/python -m pytest -q -m local -s
```

Run what CI runs locally (non-local tests):

```bash
.venv/bin/python -m pytest -q -m "not local"
```

Helpful env vars:
- `TEST_USE_AUTH_STATE=1` — tell tests to use a recorded `auth_state.json` for playback
- `PLAYWRIGHT_HEADLESS=1` — run Playwright headless

## Interactive auth-state helper (local-only)

Use this helper to record Playwright storage (cookies + localStorage) to
`auth_state.json` for local playback. Keep that file local and never commit it.

```bash
# open a headed browser you can sign into, then press ENTER in the terminal to save
.venv/bin/python scripts/dev/ensure_auth_state.py --output auth_state.json --url https://x.com/login
```

Then run local tests using the recorded state:

```bash
export TEST_USE_AUTH_STATE=1
export TEST_LOGIN_USERNAME=you@example.com
.venv/bin/python -m pytest -q -m local
```

## CI and Playwright

CI intentionally skips browser-driven tests. If maintainers need to run those
tests in CI, use the manual `Refresh Playwright Browsers` workflow to populate
the cache (Actions -> select workflow -> Run workflow).

## Contributing & dev tooling

- Use `make setup-dev` to prepare the venv and install Playwright browsers.
- Run `make pre-commit-install` (or run `.venv/bin/python -m pre_commit install`) to install git hooks.

If you'd like I can draft a short PR description summarizing these changes and push it to update the open PR.
  .venv/bin/python -m pytest -q tests/test_login_playwright.py -o playwright_browser=chromium --headed
```

The test will create a small companion meta file next to `auth_state.json`
(`auth_state.json.meta.json`) to record browser hints used during playback.
