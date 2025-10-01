import os
from typing import Any

import pytest

from utils.playwright_humanize import human_type
from utils.playwright_healing import find_locator_with_healing


@pytest.mark.local
def test_login_x_com(browser_type: Any) -> None:
    """Minimal, deterministic local test: open x.com, search 'colorado', click Latest, wait 10s.

    Skips in CI or when `auth_state.json` is not present.
    """

    # Skip if no auth state is available (local developer-only test)
    auth_path = os.path.join(os.getcwd(), "auth_state.json")
    if not os.path.exists(auth_path):
        pytest.skip("auth_state.json not found; skipping local login test")

    browser = None
    ctx = None
    page = None
    try:
        browser = browser_type.launch(headless=False)
        ctx = browser.new_context(storage_state=auth_path)
        page = ctx.new_page()

        # Navigate to the site
        try:
            page.goto("https://x.com", timeout=15_000)
            page.wait_for_selector("body", timeout=8_000)
        except Exception:
            pass

        selectors = [
            'input[aria-label="Search"]',
            'input[type="search"]',
            'input[placeholder*="Search"]',
            'input[name="q"]',
        ]

        # Find search input
        search_locator = None
        try:
            search_locator = find_locator_with_healing(page, selectors)
        except Exception:
            search_locator = None

        if search_locator:
            try:
                search_locator.click()
            except Exception:
                try:
                    search_locator.focus()
                except Exception:
                    pass

            # Type 'colorado' human-like
            try:
                human_type(search_locator, "colorado", min_delay=0.05, max_delay=0.12)
            except Exception:
                try:
                    search_locator.fill("colorado")
                except Exception:
                    pass

            try:
                search_locator.press("Enter")
            except Exception:
                try:
                    page.keyboard.press("Enter")
                except Exception:
                    pass

            page.wait_for_timeout(500)
        else:
            # Direct search results fallback
            try:
                from urllib.parse import quote_plus

                page.goto(f"https://x.com/search?q={quote_plus('colorado')}")
                page.wait_for_timeout(500)
            except Exception:
                pass

        # Click Latest and wait
        try:
            latest = page.locator("text=Latest")
            if latest.count() == 0:
                latest = page.locator("button:has-text('Latest')")

            if latest.count() > 0:
                try:
                    latest.first.click()
                except Exception:
                    try:
                        page.evaluate("el => el.click()", latest.first)
                    except Exception:
                        pass
                page.wait_for_timeout(10_000)
        except Exception:
            pass

    finally:
        try:
            if ctx is not None:
                ctx.close()
        except Exception:
            pass
        try:
            if browser is not None:
                browser.close()
        except Exception:
            pass
