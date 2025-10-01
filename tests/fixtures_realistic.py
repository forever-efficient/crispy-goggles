import pytest
from typing import Generator

from utils.playwright_utils import create_realistic_context


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

    ctx = create_realistic_context(browser)
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
