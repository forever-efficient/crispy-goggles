import pytest
from typing import Generator, Any


def _create_realistic_context(browser: Any):
    """Create a realistic browser context for local testing.

    This is a small, self-contained implementation extracted from the
    previous `utils.playwright_utils.create_realistic_context` so the test
    fixtures no longer depend on the removed `utils/` package.
    """
    # Example realistic options: enable javaScript, use a viewport, and
    # preserve default permissions. Adjust as needed for your environment.
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    return context


@pytest.fixture
def realistic_context(browser) -> Generator:
    """Yield a Playwright page created from a realistic BrowserContext.

    This fixture is intended for local development. It will be skipped in CI
    environments per project policy.
    """
    # Skip if Playwright browsers are not available in the environment.
    # This keeps the fixture safe for CI where browsers may not be installed.
    from tests.conftest import _playwright_browsers_present

    if not _playwright_browsers_present():
        pytest.skip("realistic_context requires Playwright browsers; skipping")

    ctx = _create_realistic_context(browser)
    page = ctx.new_page()
    try:
        yield page
    finally:
        try:
            page.close()
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass
