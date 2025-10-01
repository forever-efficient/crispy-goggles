from typing import Any, Optional


def create_realistic_context(browser: Any, *, storage_state: Optional[str] = None):
    """Create a realistic Playwright BrowserContext for local testing.

    This uses hard-coded, sensible defaults (no environment variables) so
    tests get a consistent, human-like context. Optionally load a saved
    `storage_state` (auth JSON) to start an authenticated session.
    """
    opts = {
        "viewport": {"width": 1280, "height": 800},
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "locale": "en-US",
        "timezone_id": "America/Denver",
        "accept_downloads": True,
        "extra_http_headers": {"accept-language": "en-US,en;q=0.9"},
    }

    if storage_state:
        opts["storage_state"] = str(storage_state)

    # Remove None values
    opts = {k: v for k, v in opts.items() if v is not None}

    ctx = browser.new_context(**opts)

    # Try to grant some common permissions for an authenticated session.
    try:
        ctx.grant_permissions(["geolocation", "notifications"], origin="https://x.com")
    except Exception:
        pass

    try:
        # Set a reasonable default timeout for actions
        ctx.set_default_timeout(30_000)
    except Exception:
        pass

    return ctx
