Title: Migrate local browser tests to Playwright + pytest and add helpers

Summary

This PR migrates local browser-driven tests from Selenium/Behave to Playwright + pytest. It includes:

- Playwright-based tests and helpers (humanize utilities, realistic context helpers, fixtures).
- Storage-state auth helpers and a fast-path for applying `auth_state.json` during local runs.
- A small CI hygiene fix: moved an inline Python heredoc from the workflow into `ci/list_local_tests.py` and added a `.vscode/settings.json` mapping for GitHub Actions schema to reduce YAML editor warnings.
- Updated README with a short migration summary and local-only test guidance.

Why

Playwright provides a modern, more reliable browser automation API and integrates well with pytest for local test runs. The changes keep browser tests local-only to avoid CI browser downloads and installs.

Testing

- Ran the non-local test suite locally: `python -m pytest -q -m "not local"` → 4 passed, 1 deselected
- The `ci/list_local_tests.py` helper is used by the CI workflow to collect tests and avoid embedding multiline heredocs in YAML.

Notes

- Browser tests are explicitly marked with `@pytest.mark.local` and are excluded from CI. To run browser tests in CI you must use the manual `Refresh Playwright Browsers` workflow to prepare caches. This is deliberate.
- Do NOT commit `auth_state.json` to the repo; it is intentionally local-only and ignored by git.

Additional follow-ups (optional)

- Add an RFC-style migration note or longer changelog entry if maintainers want a more detailed history.
- Optionally add a `--speed` toggle to the humanization helpers for faster smoke runs.
