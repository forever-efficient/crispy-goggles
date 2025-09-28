#!/usr/bin/env python3
"""Preview the realistic Playwright context locally.

Run locally to open a headed browser with the realistic context and print the
computed properties (user agent, viewport, platform hints). Intended for
developer debugging only.
"""
import time
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from utils.playwright_utils import create_realistic_context


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", help="optional storage state path", default=None)
    p.add_argument("--pause", type=int, default=10, help="seconds to keep the browser open")
    args = p.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        ctx = create_realistic_context(browser, storage_state=args.state)
        page = ctx.new_page()
        ua = page.evaluate("() => navigator.userAgent")
        viewport = page.viewport_size
        platform = page.evaluate("() => navigator.platform")
        print("User-Agent:", ua)
        print("Viewport:", viewport)
        print("Platform:", platform)
        print("Opening blank page for inspection. Close browser or wait to exit.")
        page.goto("about:blank")
        try:
            time.sleep(args.pause)
        except KeyboardInterrupt:
            pass
        try:
            ctx.close()
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
