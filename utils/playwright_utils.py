"""Helpers to create more realistic Playwright browser contexts.

These are developer-only helpers to make headed browser runs look closer to a
real user by setting common browser context options and injecting small
client-side scripts (for example to hide navigator.webdriver).

Use cautiously and only for local development; do NOT use these to bypass any
site's bot protections on CI or production systems.
"""
from typing import Optional
import random
import statistics
import json
from pathlib import Path


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)

# A small pool of realistic desktop UA strings to rotate during local runs.
USER_AGENT_POOL = [
    DEFAULT_USER_AGENT,
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]


def create_realistic_context(browser, *, storage_state: Optional[str] = None, locale: str = "en-US"):
    """Create a BrowserContext with options that resemble a real user.

    Args:
        browser: Playwright browser object (from pytest-playwright or sync API).
        storage_state: Optional path to a Playwright storage state JSON file.
        locale: locale string to set on the context.

    Returns:
        A newly created BrowserContext.
    """
    # If a storage_state path is provided, try to persist/read companion
    # metadata so repeated runs using the same storage_state look consistent.
    meta = {}
    meta_path = None
    if storage_state:
        try:
            meta_path = Path(storage_state).with_suffix(Path(storage_state).suffix + ".meta.json")
            if meta_path.exists():
                with meta_path.open("r", encoding="utf-8") as f:
                    meta = json.load(f)
        except Exception:
            meta = {}

    # Slightly randomize viewport to avoid a static fingerprint, but reuse
    # persisted values if available.
    width = meta.get("width") or random.choice([1200, 1280, 1366, 1440])
    height = meta.get("height") or random.choice([700, 768, 800, 900])

    # Pick a user agent from the pool with a small bias toward DEFAULT
    user_agent = meta.get("user_agent") or random.choice(USER_AGENT_POOL)

    # Randomize a few device/platform hints
    platform = meta.get("platform") or random.choice(["MacIntel", "Win32", "Linux x86_64"])
    # Make hardwareConcurrency and deviceMemory plausible
    hw_concurrency = meta.get("hw_concurrency") or random.choice([2, 4, 8])
    device_memory = meta.get("device_memory") or random.choice([4, 8, 16])

    ctx = browser.new_context(
        storage_state=storage_state,
        user_agent=user_agent,
        viewport={"width": width, "height": height},
        locale=locale,
        timezone_id="America/Los_Angeles",
        geolocation={"latitude": 37.7749, "longitude": -122.4194},
        permissions=["geolocation"],
        accept_downloads=True,
    )

    # Add an init script to modify simple fingerprinting surfaces before any
    # page script runs. Keep scripts minimal and non-invasive.
    init_script = r"""
    // navigator.webdriver
    try { Object.defineProperty(navigator, 'webdriver', { get: () => false }); } catch (e) {}
    // languages
    try { Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); } catch(e) {}
    // plugins
    try { Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] }); } catch(e) {}
    // chrome object (basic shape)
    try { window.chrome = window.chrome || { runtime: {} }; } catch(e) {}
    // permissions query shim for geolocation
    try {
      const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
      if (originalQuery) {
        window.navigator.permissions.query = (parameters) => (
          parameters.name === 'geolocation' ? Promise.resolve({ state: 'granted' }) : originalQuery(parameters)
        );
      }
    } catch(e) {}
    """

    try:
        ctx.add_init_script(init_script)
    except Exception:
        # older Playwright versions or unsupported contexts may raise; ignore
        pass

    # Helpful default headers
    try:
        ctx.set_extra_http_headers({"Accept-Language": "en-US,en;q=0.9"})
    except Exception:
        pass

    # Try to set additional context-level hints where supported (best-effort)
    try:
        ctx.add_init_script(
            f"window.__pw_platform = '{platform}'; window.__pw_hw = {hw_concurrency}; window.__pw_dm = {device_memory};"
        )
    except Exception:
        pass

    # Persist choices back to companion metadata next to storage_state for
    # subsequent runs. Best-effort only.
    if meta_path is not None:
        try:
            meta_to_write = {
                "width": width,
                "height": height,
                "user_agent": user_agent,
                "platform": platform,
                "hw_concurrency": hw_concurrency,
                "device_memory": device_memory,
            }
            with meta_path.open("w", encoding="utf-8") as f:
                json.dump(meta_to_write, f)
        except Exception:
            pass

    return ctx
