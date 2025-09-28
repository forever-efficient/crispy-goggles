"""Open a headed Chromium using a saved Playwright storage state and navigate to a URL.

Usage:
  .venv/bin/python scripts/show_auth_state.py --state auth_state.json --url https://x.com --pause 8

This is a local-only helper for debugging; it intentionally runs headed so you can
watch the browser.
"""
from pathlib import Path
from argparse import ArgumentParser
from playwright.sync_api import sync_playwright


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--state", default="auth_state.json", help="Path to storage state JSON")
    parser.add_argument("--url", default="https://x.com", help="URL to open")
    parser.add_argument("--pause", type=int, default=8, help="Seconds to wait while showing the page")
    args = parser.parse_args()

    state_path = Path(args.state)
    if not state_path.exists():
        print(f"Storage state file not found: {state_path}")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        try:
            ctx = browser.new_context(storage_state=str(state_path))
            page = ctx.new_page()
            print(f"Opening {args.url} with storage state {state_path}")
            """Shim wrapper for backward compatibility to `scripts/dev/show_auth_state.py`."""
            import os
            import runpy
            import sys

            HERE = os.path.dirname(__file__)
            TARGET = os.path.join(HERE, "dev", "show_auth_state.py")

            if __name__ == "__main__":
                if not os.path.exists(TARGET):
                    print(f"Expected dev script not found: {TARGET}")
                    sys.exit(2)
                runpy.run_path(TARGET, run_name="__main__")
            except Exception:
