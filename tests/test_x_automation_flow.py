import os
from pathlib import Path
from typing import Any, Optional

import pytest
import time

from utils.playwright_humanize import human_type, simulate_micro_interactions


@pytest.mark.local
def test_x_flow(browser_type: Any) -> None:
    """Top-level test orchestrating small helper steps.

    Helpers: apply_auth_state, navigate_and_wait_for_page, find_search_locator,
    human_search_and_submit, click_latest_if_present.
    """

    # Local-only test; skip only if auth_state.json is missing

    # Resolve auth_state.json relative to the repository root so the test
    # behaves the same when run as a single file or as part of the full suite.
    repo_root = Path(__file__).resolve().parents[1]
    auth_path = str(repo_root / "auth_state.json")

    # Helpful debug info if the file isn't found when running the full suite
    if not os.path.exists(auth_path):
        print(f"[debug] cwd={os.getcwd()} repo_root={repo_root} auth_path_exists=False")
        pytest.skip("auth_state.json not found; skipping local test")
    else:
        print(f"[debug] using auth_path={auth_path}")

    browser = None
    ctx = None
    page = None
    try:
        browser, ctx, page = apply_auth_state(browser_type, auth_path)

        navigate_and_wait_for_page(page, "https://x.com", wait_ms=5_000)

        selectors = [
            'input[aria-label="Search"]',
            'input[type="search"]',
            'input[placeholder*="Search"]',
            'input[name="q"]',
        ]

        search = find_search_locator(page, selectors)
        if search is not None:
            human_search_and_submit(page, search, query="colordo")
        else:
            # fallback to direct search URL
            try:
                from urllib.parse import quote_plus

                page.goto(f"https://x.com/search?q={quote_plus('colordo')}")
            except Exception:
                pass

        click_latest_if_present(page, pause_ms=2000)

        # brief pause so developer can visually confirm the result
        page.wait_for_timeout(3000)
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
    # Simpler navigation per user request: go to the homepage and wait exactly 10s
    try:
        page.goto(url, timeout=max(timeout, 30_000))
        print(f"[debug][{time.time():.3f}] goto start -> {url}")
    except Exception:
        # navigation may fail silently in some environments; continue to wait anyway
        print(f"[debug][{time.time():.3f}] goto failed for {url}")
        pass

    # Show the URL we landed on so runs can be diagnosed easily in stdout
    try:
        print(f"[debug][{time.time():.3f}] after initial goto: {page.url}")
    except Exception:
        pass

    # If the stored session or client-side script redirected us to search/results,
    # force a navigation back to the homepage so the subsequent search step starts there.
    try:
        current = page.url or ""
        if "/search" in current or not current.startswith("https://x.com"):
            try:
                print(
                    f"[debug] detected non-homepage URL, forcing homepage navigation: {current}"
                )
            except Exception:
                pass
            try:
                page.goto(url, timeout=max(timeout, 30_000))
                print(f"[debug][{time.time():.3f}] forced homepage goto -> {url}")
            except Exception:
                try:
                    page.goto(url, timeout=max(timeout, 30_000))
                    print(
                        f"[debug][{time.time():.3f}] forced homepage goto (retry) -> {url}"
                    )
                except Exception:
                    print(f"[debug][{time.time():.3f}] forced homepage goto failed")
                    pass
            # wait a bit for homepage to settle and try to detect a header/nav
            try:
                page.wait_for_selector('nav, header, [role="banner"]', timeout=8_000)
            except Exception:
                pass
            try:
                print(f"[debug] after forcing homepage nav: {page.url}")
            except Exception:
                pass
    except Exception:
        pass

    # Force an explicit pause so the page is fully settled before the search step
    print(
        f"[debug][{time.time():.3f}] waiting for {max(wait_ms, 1_000)} ms before search"
    )
    page.wait_for_timeout(max(wait_ms, 1_000))


def find_search_locator(page: Any, selectors: list) -> Optional[Any]:
    """Return the first locator matching selectors or None."""
    # Fast non-blocking pass: check currently present elements without waiting
    for sel in selectors:
        try:
            el = page.query_selector(sel)
            if el:
                print(f"[debug][{time.time():.3f}] quick-pass found selector: {sel}")
                loc = page.locator(sel).first
                try:
                    if loc.count() > 0 and loc.is_visible():
                        return loc
                except Exception:
                    return loc
        except Exception:
            continue

    # If nothing is present immediately, do one combined short wait instead of per-selector waits.
    combined = ",".join(selectors)
    try:
        print(f"[debug][{time.time():.3f}] combined wait for selectors: {combined}")
        page.wait_for_selector(combined, timeout=3_000)
        # return the first matching locator
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
        # Don't run heavy micro-interactions before typing; they cause a visible delay.
        # We'll run a light micro-interaction after submitting instead.
        # Ensure input is focused/clicked before typing
        try:
            # ensure the locator is visible/attached to avoid race conditions
            try:
                locator.wait_for(state="visible", timeout=2_000)
            except Exception:
                pass
            print(f"[debug][{time.time():.3f}] focusing search input")
            locator.click()
        except Exception:
            print(f"[debug][{time.time():.3f}] locator.click() failed; continuing")
            pass

        # Prefer the fast fill API when available to reduce per-character delay.
        try:
            print(f"[debug][{time.time():.3f}] filling query: {query}")
            locator.fill(query)
            # post-fill debug: read back value
            try:
                val = locator.input_value()
                print(f"[debug][{time.time():.3f}] post-fill input_value: {val}")
            except Exception:
                try:
                    val = locator.evaluate("el => el.value")
                    print(f"[debug][{time.time():.3f}] post-fill eval value: {val}")
                except Exception:
                    print(
                        f"[debug][{time.time():.3f}] post-fill value retrieval failed"
                    )
        except Exception:
            print(
                f"[debug][{time.time():.3f}] locator.fill failed; falling back to human_type"
            )
            # fall back to humanized typing when fill isn't available
            human_type(locator, query, min_delay=0.02, max_delay=0.06)
            try:
                val = locator.input_value()
                print(f"[debug][{time.time():.3f}] post-human_type input_value: {val}")
            except Exception:
                try:
                    val = locator.evaluate("el => el.value")
                    print(
                        f"[debug][{time.time():.3f}] post-human_type eval value: {val}"
                    )
                except Exception:
                    print(
                        f"[debug][{time.time():.3f}] post-human_type value retrieval failed"
                    )

        try:
            locator.press("Enter")
        except Exception:
            try:
                page.keyboard.press("Enter")
            except Exception:
                pass

        # After submitting, wait for either the search URL to appear or the network to settle.
        try:
            print(f"[debug][{time.time():.3f}] waiting for search url or networkidle")
            page.wait_for_url("**/search**", timeout=5_000)
        except Exception:
            try:
                page.wait_for_load_state("networkidle", timeout=5_000)
            except Exception:
                pass
        # perform a lightweight micro-interaction after submitting so the session still looks human
        # lightweight post-submit pause so results render visibly
        try:
            page.wait_for_timeout(100)
        except Exception:
            pass
    except Exception:
        # keep original tolerant behavior
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
