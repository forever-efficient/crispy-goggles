#!/usr/bin/env python3
"""Helper to launch a headed Chromium with auth_state.json for local observation.

This runs in a separate process to avoid asyncio / sync API conflicts when
pytest's event loop is active. It opens a browser, navigates to x.com using
the provided storage-state, waits briefly so the developer can observe, then
closes.
"""

import os
import time

try:
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover - helper used interactively
    print("playwright.sync_api not available:", exc)
    raise


def main():
    auth_path = os.path.join(os.getcwd(), "auth_state.json")
    if not os.path.exists(auth_path):
        print("auth_state.json not found; nothing to do")
        return

    with sync_playwright() as pw:
        # Launch Chromium headed
        browser = pw.chromium.launch(headless=False)
        # Create a context from the storage state so session is applied
        ctx = browser.new_context(storage_state=auth_path)
        page = ctx.new_page()
        try:
            page.goto("https://x.com")
        except Exception as e:
            print("navigate error:", e)

        print("Launched headed Chromium with auth_state.json — visible for 6s")
        # Give the developer time to see the window
        time.sleep(6)

        try:
            ctx.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
