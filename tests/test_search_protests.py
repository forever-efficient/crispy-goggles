import os
from pathlib import Path
from typing import Any

import pytest
from tests.dev_context import create_realistic_context

# IMPORTANT: Never disable manual auth debug mode. This constant is intentionally
# defined at module scope and the test will refuse to run if it is False.
DEBUG_MANUAL_AUTH: bool = True

if not DEBUG_MANUAL_AUTH:
    raise RuntimeError(
        "DEBUG_MANUAL_AUTH must be True for local interactive runs — do not change this."
    )


@pytest.mark.local
def test_search_protests(browser_type: Any) -> None:
    """Use stored session to navigate to a focused X search, click Latest, and save HTML.

    This test is local-only and expects `auth_state.json` at repo root.
    """
    repo_root = Path(__file__).resolve().parents[1]
    auth_path = str(repo_root / "auth_state.json")

    # Debug mode is enforced at module-level; do not set here.

    browser = browser_type.launch(headless=False)
    # Use the realistic context which applies UA, timezone, headers, and storage
    # Load storage_state only if the auth file exists; otherwise create a fresh context.
    if os.path.exists(auth_path):
        ctx = create_realistic_context(browser, storage_state=auth_path)
        storage_provided = True
    else:
        ctx = create_realistic_context(browser, storage_state=None)
        storage_provided = False
    page = ctx.new_page()

    # Basic validations to ensure context looks human-like
    try:
        ua = page.evaluate("() => navigator.userAgent")
    except Exception:
        ua = None
    try:
        tz = page.evaluate("() => Intl.DateTimeFormat().resolvedOptions().timeZone")
    except Exception:
        tz = None

    # Check that the UA and timezone are set to our realistic defaults
    assert ua is None or "Chrome" in ua
    assert tz is None or "America/Denver" in tz

    # Validate storage_state contains an auth_token cookie when storage was provided
    if storage_provided:
        try:
            cookies = ctx.cookies()
        except Exception:
            cookies = []
        assert any(c.get("name") == "auth_token" for c in cookies), (
            "auth_token cookie missing from storage_state"
        )

    try:
        # encode the query exactly as requested
        url = "https://x.com/search?q=(protest%20OR%20rally%20OR%20demonstration%20OR%20gun%20OR%20shoot%20OR%20dead%20OR%20kill%20OR%20plug%20OR%20fetty%20OR%20arrest%20OR%20seize%20OR%20bomb)%20(aurora%20OR%20denver%20OR%20arapahoe)&src=typed_query&f=live"
        page.goto(url, timeout=60_000)

        # give results a moment to render
        page.wait_for_timeout(3_000)

        # After navigating, check if we've been redirected to a login page.
        # Common cues: presence of "Log in" / "Sign in" text or a login form.
        def looks_like_login(p):
            try:
                # check for typical login text
                if p.locator("text=Log in").count() > 0:
                    return True
                if p.locator("text=Sign in").count() > 0:
                    return True
                # sometimes there is an input with type password on a login page
                if p.locator("input[type='password']").count() > 0:
                    return True
            except Exception:
                return False
            return False

        if looks_like_login(page):
            # If login detected, try a fallback auth file (recorded by manual auth)
            alt_auth = str(repo_root / "auth_state.json")
            # If there's a recorded alt auth file and we're not forcing manual auth, use it.
            if os.path.exists(alt_auth) and not DEBUG_MANUAL_AUTH:
                try:
                    # close current context and create a new one with the alternate storage
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    ctx = create_realistic_context(browser, storage_state=alt_auth)
                    page = ctx.new_page()

                    # retry navigation with the authenticated context
                    page.goto(url, timeout=60_000)
                    page.wait_for_timeout(3_000)
                except Exception:
                    # fall through to attempt continuing unauthenticated
                    pass
            else:
                # No recorded auth available — pause and let the human log in manually.
                # The browser is headed (headless=False), so present instructions and wait.
                print(
                    "Login page detected. Please complete manual login in the opened browser window."
                )
                input(
                    "After completing login, press Enter here to continue and save storage_state..."
                )

                # Attempt to write storage_state from the current context to the alt_auth path.
                try:
                    # Playwright BrowserContext has a storage_state(path=...) method
                    ctx.storage_state(path=alt_auth)
                except Exception:
                    # older versions may require ctx.storage_state() -> dict and write manually
                    try:
                        state = ctx.storage_state()
                        with open(alt_auth, "w", encoding="utf-8") as stf:
                            import json

                            json.dump(state, stf)
                    except Exception:
                        # If saving fails, proceed without persisting but attempt to continue
                        pass

                # Close and recreate context with the saved storage (best-effort)
                try:
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    if os.path.exists(alt_auth):
                        ctx = create_realistic_context(browser, storage_state=alt_auth)
                        page = ctx.new_page()
                        page.goto(url, timeout=60_000)
                        page.wait_for_timeout(3_000)
                except Exception:
                    # If anything goes wrong, continue with the existing unauthenticated context
                    pass

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
