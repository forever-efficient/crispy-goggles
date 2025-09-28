<!-- .github/copilot-instructions.md - Guidance for AI coding agents working on crispy-goggles -->
# Quick orientation (20-30s)

-- This repository is a small Python automation project using pytest + Playwright (browser automation).
# What matters for edits or feature work

-- Use the existing test pattern: pytest tests under `tests/` that use the `page` fixture from `pytest-playwright`.
# How to run tests locally (developer workflow)

-- Install dependencies: this repo expects Python with Playwright installed. Example (macOS / zsh):
```bash
# create venv and activate
python -m venv .venv
source .venv/bin/activate
make setup
playwright install  # install browsers
```

-- Run the whole test suite with pytest from the repo root:
```bash
pytest -q
```

- If tests hang or a browser process is left behind, ensure `context.browser.close()` in `after_scenario` runs (see `features/environment.py`).
# Project-specific conventions and patterns

-- Minimal project: pytest is the test runner and pytest-playwright provides browser fixtures.
# Files to open first when making changes

-- `tests/test_login_playwright.py` — Playwright-based login test. Use it as a migration example.
# Idiomatic code edits for agents

- When changing step implementations, preserve the use of `context.page` from `environment.py` rather than instantiating Playwright again.
# Integration and external dependencies

- External services: none by design. Tests exercise `https://the-internet.herokuapp.com/` in existing scenarios.

## CI layout (GitHub Actions)

- The repository CI has three logical jobs in `.github/workflows/ci.yml`:
	- `browsers`: installs Playwright browsers and caches them (runs once per workflow run).
		- `browsers`: installs and caches Playwright browsers and runs once per workflow run.
		- `pytest-playwright`: runs pytest with Playwright fixtures.

# To reproduce CI locally:
```bash
# create venv and install deps
make setup
# install browsers (only needed once)
make install-browsers
# run unit tests
pytest -q
```

Note: The README contains step-by-step instructions for adding the required repository secrets (SMTP and Slack) used by the refresh workflow.
# Example edits an AI might make (concrete)

- Improve locator healing: add a short timeout and call `element.count()` or `element.first` before `is_visible()` to avoid false negatives.

# What not to change without human review

- Don’t change `features/environment.py` to use a different browser engine or headless setting without updating README and CI (no CI config present).
- Don’t remove existing baseline images (e.g., `login_page_baseline.png`) — they may be used as manual visual references.

# Where to leave notes for humans

- Edit the `README.md` with setup steps if you change how tests are run; dependencies are declared in `pyproject.toml` and installed via `make setup`.
-- If you add cross-cutting changes (e.g., change the way Playwright is launched), update `tests/conftest.py` and mention it in the README and this file.

---
If anything above is unclear or you'd like the instructions expanded (for example adding more setup steps), tell me which area to expand and I'll update this file.

## CI refresh job and notifications

- There is a scheduled workflow `.github/workflows/refresh-browsers.yml` that runs daily to refresh the Playwright browser cache. It uses the same cache key pattern as the CI `browsers` job.
- The refresh job will send an email on failure using SMTP secrets. To enable notifications, add the following repository secrets:
	- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFY_EMAIL`.

## CI logs & quick troubleshooting checklist

- Actions UI (CI run logs): https://github.com/forever-efficient/crispy-goggles/actions

- Quick local checklist to reproduce CI failures:
	1. Create and activate a venv: `python -m venv .venv && source .venv/bin/activate`
	2. Install deps: `make setup`
	3. (If failing Playwright runs) install browsers: `playwright install`
	4. Run unit tests: `pytest -q`
	5. Run pytest: `pytest -q`


