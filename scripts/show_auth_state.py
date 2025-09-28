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
            page.goto(args.url)
            # basic checks
            try:
                has_auth = any(c.get('name') == 'auth_token' for c in ctx.cookies())
            except Exception:
                has_auth = False
            print(f"Has auth_token cookie in context? {has_auth}")
            print(f"Page URL: {page.url}")
            # wait so the user can observe the headed browser
            page.wait_for_timeout(args.pause * 1000)
        finally:
            try:
                ctx.close()
            except Exception:
                pass
            browser.close()


if __name__ == "__main__":
    main()
