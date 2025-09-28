"""Ensure a Playwright storage state file exists by launching a headed browser.

This is an interactive helper intended for local development only. It will
open Chromium (headed), navigate to the supplied login URL, then wait for the
developer to sign in and press ENTER in the terminal to save the storage
state to disk.

Do NOT run this in CI. The calling code (tests/conftest.py) will only invoke
this script when it detects a non-CI environment.

Example:
  .venv/bin/python scripts/ensure_auth_state.py --output=auth_state.json

"""
"""Shim wrapper for backward compatibility.

The real implementations live under `scripts/dev/`. This shim executes the
dev script so existing commands continue to work while keeping the real
helpers in a dev-only folder.
"""
import os
import runpy
import sys

HERE = os.path.dirname(__file__)
TARGET = os.path.join(HERE, "dev", "ensure_auth_state.py")


def main() -> None:
  if not os.path.exists(TARGET):
    print(f"Expected dev script not found: {TARGET}")
    sys.exit(2)
  runpy.run_path(TARGET, run_name="__main__")


if __name__ == "__main__":
  main()
