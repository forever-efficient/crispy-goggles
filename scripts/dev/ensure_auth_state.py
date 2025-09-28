"""Ensure a Playwright storage state file exists by launching a headed browser.

This is an interactive helper intended for local development only. It will
open Chromium (headed), navigate to the supplied login URL, then wait for the
developer to sign in and press ENTER in the terminal to save the storage
state to disk.

Do NOT run this in CI. The calling code (tests/conftest.py) will only invoke
this script when it detects a non-CI environment.

Example:
  .venv/bin/python scripts/dev/ensure_auth_state.py --output=auth_state.json

"""
from pathlib import Path
from argparse import ArgumentParser
from playwright.sync_api import sync_playwright


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--output", default="auth_state.json", help="Path to write storage state JSON")
    parser.add_argument("--url", default="https://x.com/login", help="URL to open for manual sign-in")
    args = parser.parse_args()

    out = Path(args.output)
    print("This helper is interactive and intended for local development only.")
    print("A headed Chromium will open. Please sign in manually, then return here and press ENTER to save the storage state.")
    print("If you prefer to close the browser window instead of pressing ENTER, that also saves the state.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(args.url)

        try:
            # Wait for user input in the terminal. If the user closes the browser,
            # an exception can be raised when attempting to interact; we'll handle it.
            input("After signing in, press ENTER here to save storage state and exit...\n")
        except Exception:
            # ignore
            pass

        try:
            ctx.storage_state(path=str(out))
            print(f"Wrote storage state to {out}")
        except Exception as e:
            print(f"Failed to write storage state: {e}")

        try:
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()

