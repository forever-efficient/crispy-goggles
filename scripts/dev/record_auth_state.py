"""Record Playwright storage state (cookies + localStorage) to a JSON file.

Run this script with the project's venv, open the headed browser, sign in manually,
then close the browser window. The script will save a storage file you can reuse
in tests via the TEST_USE_AUTH_STATE env var.

Example:
  .venv/bin/python scripts/dev/record_auth_state.py --output=auth_state.json

Be careful: do not commit real secrets to the repository. Keep the saved file out
of VCS or add it to .gitignore.
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        print(f"Open browser, navigate to {args.url} and sign in manually. Close the browser when done.")
        page.goto(args.url)
        try:
            # wait until the user closes the browser window (we poll)
            while True:
                page.wait_for_timeout(1000)
        except Exception:
            # context/browser closed by user
            pass

        # Save storage state
        ctx.storage_state(path=str(out))
        print(f"Wrote storage state to {out}")


if __name__ == "__main__":
    main()
