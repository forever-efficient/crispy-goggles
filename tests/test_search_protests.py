import os
from pathlib import Path
from typing import Any

import pytest


@pytest.mark.local
def test_search_protests(browser_type: Any) -> None:
    """Use stored session to navigate to a focused X search, click Latest, and save HTML.

    This test is local-only and expects `auth_state.json` at repo root.
    """
    repo_root = Path(__file__).resolve().parents[1]
    auth_path = str(repo_root / "auth_state.json")

    if not os.path.exists(auth_path):
        pytest.skip("auth_state.json not found; skipping local test")

    browser = browser_type.launch(headless=False)
    ctx = browser.new_context(storage_state=auth_path)
    page = ctx.new_page()

    try:
        # encode the query exactly as requested
        url = (
            "https://x.com/search?q=(protest%20OR%20rally%20OR%20demonstration%20OR%20gun%20OR%20shoot%20OR%20dead%20OR%20kill%20OR%20plug%20OR%20fetty%20OR%20arrest%20OR%20seize%20OR%20bomb)%20(aurora%20OR%20denver%20OR%20arapahoe)&src=typed_query&f=live"
        )
        page.goto(url, timeout=60_000)

        # give results a moment to render
        page.wait_for_timeout(3_000)

        # Click "Latest" if present
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

        # save HTML
        results_dir = Path("artifacts/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        out_path = results_dir / "search_protests.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(page.content())

    finally:
        try:
            ctx.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass
