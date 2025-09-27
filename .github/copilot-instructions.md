<!-- .github/copilot-instructions.md - Guidance for AI coding agents working on crispy-goggles -->
# Quick orientation (20-30s)

- This repository is a small Python automation project using Behave (BDD) + Playwright (browser automation).
- Tests live under `features/` (Gherkin `.feature` files + step definitions in `features/steps/`).
- Test browser lifecycle is managed in `features/environment.py` (Playwright is started/stopped there).

# What matters for edits or feature work

- Use the existing test pattern: Gherkin scenarios in `features/*.feature` -> step implementations in `features/steps/*.py`.
- Keep Playwright page lifecycle consistent: `before_all` starts Playwright, `before_scenario` launches a browser and creates `context.page`, `after_scenario` closes it.
- Locator resiliency is centralized in `utils/healing_locators.py`. Prefer `find_element_with_healing(page, [...])` for selectors that may change; follow its simple "try each selector" behaviour.

# How to run tests locally (developer workflow)

- Install dependencies: this repo expects Python with Playwright and Behave installed. Example (macOS / zsh):

```bash
# create venv and activate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present; otherwise pip install behave playwright
playwright install  # install browsers
```

- Run the whole suite with Behave from the repo root:

```bash
behave
```

- If tests hang or a browser process is left behind, ensure `context.browser.close()` in `after_scenario` runs (see `features/environment.py`).

# Project-specific conventions and patterns

- Minimal project: no test runner wrapper or test config file (e.g., pytest). Behave is the default runner.
- Steps should be small and focused: page navigation in `Given`, interactions in `When`, assertions in `Then`.
- Visual baseline artifacts (example: `login_page_baseline.png`) may be created manually by tests — these are checked into the repo. When adding visual checks, document where screenshots are saved.
- Locator healing: `find_element_with_healing(page, locators)` returns a Playwright Locator if any of the provided selectors matches and is visible. It prints which locator succeeded and raises if none match. Use it for inputs, buttons, and other interactable elements.

# Files to open first when making changes

- `features/login.feature` — example Gherkin flow.
- `features/steps/login_steps.py` — real step implementations; shows how `find_element_with_healing` is used and where screenshots are taken.
- `features/environment.py` — Playwright lifecycle; any changes to browser or context creation belong here.
- `utils/healing_locators.py` — central helper for selector fallback logic.

# Idiomatic code edits for agents

- When changing step implementations, preserve the use of `context.page` from `environment.py` rather than instantiating Playwright again.
- Use Playwright's `locator(selector)` and `is_visible()` checks as shown in `utils/healing_locators.py`.
- Avoid adding global state outside `context` (Behave uses `context` to share per-scenario objects).

# Integration and external dependencies

- External services: none by design. Tests exercise `https://the-internet.herokuapp.com/` in existing scenarios.
- Runtime dependencies: Behave, Playwright and their transitive packages. The repo does not include a `requirements.txt`; if you add one, pin versions.
 - Runtime dependencies: Behave, Playwright and their transitive packages. A minimal `requirements.txt` is provided at the repo root.
 - Use the included `Makefile` and `scripts/setup.sh` to standardize environment setup. `make setup` will create a venv and install pinned packages; `make install-browsers` will run `playwright install`.

## CI layout (GitHub Actions)

- The repository CI has three logical jobs in `.github/workflows/ci.yml`:
	- `unit`: runs `pytest` (fast) and installs Python dependencies.
	- `browsers`: installs Playwright browsers and caches them (runs once per workflow run).
	- `behave`: restores the Playwright browser cache and runs the full Behave suite (runs on PRs and pushes).

- To reproduce CI locally:

```bash
# create venv and install deps
make setup
# install browsers (only needed once)
make install-browsers
# run unit tests
pytest -q
# run behave
behave -f pretty
```

Note: The README contains step-by-step instructions for adding the required repository secrets (SMTP and Slack) used by the refresh workflow.

# Example edits an AI might make (concrete)

- Improve locator healing: add a short timeout and call `element.count()` or `element.first` before `is_visible()` to avoid false negatives.
- Add a new scenario in `features/*.feature` and implement steps in `features/steps/*` following the existing pattern.
- Add CLI helper scripts or a `Makefile` to standardize setup and `playwright install` steps.

# What not to change without human review

- Don’t change `features/environment.py` to use a different browser engine or headless setting without updating README and CI (no CI config present).
- Don’t remove existing baseline images (e.g., `login_page_baseline.png`) — they may be used as manual visual references.

# Where to leave notes for humans

- Edit the `README.md` with setup steps if you add a `requirements.txt` or change how tests are run.
- If you add cross-cutting changes (e.g., change the way Playwright is launched), update `features/environment.py` and mention it in the README and this file.

---
If anything above is unclear or you'd like the instructions expanded (for example adding a sample `requirements.txt` or a Makefile), tell me which area to expand and I'll update this file.

## CI refresh job and notifications

- There is a scheduled workflow `.github/workflows/refresh-browsers.yml` that runs daily to refresh the Playwright browser cache. It uses the same cache key pattern as the CI `browsers` job.
- The refresh job will send an email on failure using SMTP secrets. To enable notifications, add the following repository secrets:
	- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `NOTIFY_EMAIL`.

## CI logs & quick troubleshooting checklist

- Actions UI (CI run logs): https://github.com/forever-efficient/crispy-goggles/actions

- Quick local checklist to reproduce CI failures:
	1. Create and activate a venv: `python -m venv .venv && source .venv/bin/activate`
	2. Install deps: `pip install -r requirements.txt`
	3. (If failing Playwright runs) install browsers: `playwright install`
	4. Run unit tests: `pytest -q`
	5. Run Behave: `behave -f pretty`


