import os
import pytest
from typing import Generator

from utils.playwright_utils import create_realistic_context


@pytest.fixture
def realistic_context(browser) -> Generator:
    """Yield a Playwright page created from a realistic BrowserContext.

    This fixture is intended for local development. It will be skipped in CI
    environments per project policy.
    """
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or os.getenv("GITLAB_CI"):
        pytest.skip("realistic_context is disabled in CI (local-only)")

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
