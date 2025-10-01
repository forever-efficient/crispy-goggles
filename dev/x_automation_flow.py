import os
from pathlib import Path
from typing import Any, Optional

import time

from utils.playwright_humanize import human_type, simulate_micro_interactions


def apply_auth_state(browser_type: Any, auth_path: str):
    """Launch headed browser and return (browser, context, page) using storage_state."""
    browser = browser_type.launch(headless=False)
    ctx = browser.new_context(storage_state=auth_path)
    page = ctx.new_page()
    return browser, ctx, page


def navigate_and_wait_for_page(
    page: Any, url: str = "https://x.com", timeout: int = 15_000, wait_ms: int = 5_000
) -> None:
    """Navigate to url, wait for body and then wait an extra pause (ms)."""
    try:
        page.goto(url, timeout=max(timeout, 30_000))
    except Exception:
        pass
    try:
        current = page.url or ""
        if "/search" in current or not current.startswith("https://x.com"):
            try:
                page.goto(url, timeout=max(timeout, 30_000))
            except Exception:
                pass
            try:
                page.wait_for_selector('nav, header, [role="banner"]', timeout=8_000)
            except Exception:
                pass
    except Exception:
        pass

    page.wait_for_timeout(max(wait_ms, 1_000))


def find_search_locator(page: Any, selectors: list) -> Optional[Any]:
    """Return the first locator matching selectors or None."""
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                loc = page.locator(sel).first
                try:
                    if loc.count() > 0 and loc.is_visible():
                        return loc
                except Exception:
                    return loc
        except Exception:
            continue

    combined = ",".join(selectors)
    try:
        page.wait_for_selector(combined, timeout=3_000)
        for sel in selectors:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0 and loc.is_visible():
                    return loc
            except Exception:
                continue
    except Exception:
        pass

    return None


def human_search_and_submit(page: Any, locator: Any, query: str = "colordo") -> None:
    """Perform micro interactions then type query human-like and submit."""
    try:
        try:
            locator.click()
        except Exception:
            pass

        try:
            locator.fill(query)
        except Exception:
            human_type(locator, query, min_delay=0.02, max_delay=0.06)

        try:
            locator.press("Enter")
        except Exception:
            try:
                page.keyboard.press("Enter")
            except Exception:
                pass

        try:
            page.wait_for_url("**/search**", timeout=5_000)
        except Exception:
            try:
                page.wait_for_load_state("networkidle", timeout=5_000)
            except Exception:
                pass
        try:
            page.wait_for_timeout(100)
        except Exception:
            pass
    except Exception:
        pass


def click_latest_if_present(page: Any, pause_ms: int = 2000) -> None:
    """Click the 'Latest' control if present and wait a short pause."""
    try:
        latest = page.locator("text=Latest")
        if latest.count() == 0:
            latest = page.locator("button:has-text('Latest')")

        if latest.count() > 0:
            try:
                simulate_micro_interactions(page)
            except Exception:
                pass
            try:
                latest.first.click()
            except Exception:
                try:
                    page.evaluate("el => el.click()", latest.first)
                except Exception:
                    pass
            page.wait_for_timeout(pause_ms)
    except Exception:
        pass
