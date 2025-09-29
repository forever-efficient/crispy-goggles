import os
from typing import Any

import pytest

from utils.playwright_humanize import human_type, simulate_micro_interactions

# Always skip collecting this file in CI environments to ensure it never runs in CI
if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
    pytest.skip("File skipped in CI - local-only headed test", allow_module_level=True)


@pytest.mark.local
def test_x_flow(browser_type: Any) -> None:
    """Navigate to X with stored session, wait 5s, type 'colordo' into search and submit.

    Launches a headed browser explicitly (headless=False) so runs are visible.
    """

    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        pytest.skip("Local-only test skipped in CI")

    auth_path = os.path.join(os.getcwd(), "auth_state.json")
    if not os.path.exists(auth_path):
        pytest.skip("auth_state.json not found; skipping local test")

    browser = None
    ctx = None
    page = None
    try:
        # Launch headed browser explicitly
        browser = browser_type.launch(headless=False)
        ctx = browser.new_context(storage_state=auth_path)
        page = ctx.new_page()

        page.goto("https://x.com", timeout=15_000)
        # wait 5 seconds on the main page
        page.wait_for_timeout(5_000)

        # find search input and type the typo 'colordo'
        selectors = [
            'input[aria-label="Search"]',
            'input[type="search"]',
            'input[placeholder*="Search"]',
            'input[name="q"]',
        ]

        search = None
        for sel in selectors:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0:
                    search = loc
                    break
            except Exception:
                continue

        if search is not None:
            try:
                search.click()
            except Exception:
                try:
                    search.focus()
                except Exception:
                    pass
            try:
                # do a few small micro interactions before typing
                try:
                    simulate_micro_interactions(page, hover_selector=sel)
                except Exception:
                    pass
                human_type(search, "colordo", min_delay=0.02, max_delay=0.06)
            except Exception:
                try:
                    page.keyboard.type("colordo")
                except Exception:
                    pass
            try:
                search.press("Enter")
            except Exception:
                try:
                    page.keyboard.press("Enter")
                except Exception:
                    pass
        else:
            try:
                from urllib.parse import quote_plus

                page.goto(f"https://x.com/search?q={quote_plus('colordo')}")
            except Exception:
                pass

        # small micro-interactions and short pause so user can see results
        try:
            simulate_micro_interactions(page)
        except Exception:
            pass
        page.wait_for_timeout(2_000)

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
