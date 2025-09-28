# Changelog

All notable changes to this repository will be documented in this file.

## Unreleased - 2025-09-26
- Remove `requirements.txt` and consolidate dependency management into `pyproject.toml`.
- Update CI and scheduled workflows to use `pyproject.toml` in cache keys instead of `requirements.txt`.
- Update `scripts/setup.sh` to install the project editable (`pip install -e '.[dev]'`) and keep Playwright browser install.
- Update onboarding docs: add `Quick setup` and `FAQ` entries to `README.md` explaining the change.
- Update `.github/copilot-instructions.md` to recommend `make setup` and reference `pyproject.toml`.
- Update `setup.cfg` to reflect the new packaging guidance.

These changes simplify dependency and packaging workflows and align local development with CI.


## Unreleased - 2025-09-28
- Add Playwright migration: realistic browser context helpers, human-like interaction utilities, and a fast playback path using `auth_state.json` to speed up local login tests.
- Update `tests/test_login_playwright.py` with timing tuning, visible search typing, and clicking the 'Latest' control for manual verification.
- Add developer README notes for running local Playwright tests.
- CI: explicitly list local-only tests for visibility and ensure Playwright/browser tests are excluded from normal CI runs.
