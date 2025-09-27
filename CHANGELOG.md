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
