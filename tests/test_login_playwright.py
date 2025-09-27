import os
import pytest

from utils.playwright_healing import find_locator_with_healing


@pytest.mark.local
def test_login_x_com(page):
    """Login to x.com using Playwright and environment credentials.

    This mirrors the previous Behave scenario but uses Playwright's Python API
    and pytest-playwright's `page` fixture.
    """
    username = os.getenv("TEST_LOGIN_USERNAME")
    password = os.getenv("TEST_LOGIN_PASSWORD")
    if not username or not password:
        pytest.skip("TEST_LOGIN_USERNAME/TEST_LOGIN_PASSWORD not set; skipping local test")

    page.goto("https://x.com")

    login_btn = find_locator_with_healing(page, [
        'a[aria-label="Log in"]',
        'a[href*="/login"]',
        'text=Log in',
    ])
    login_btn.click()

    # Fill username/password using playwight locators
    page.wait_for_timeout(1000)
    # Fill username and password fields with healing locators
    try:
        user_in = find_locator_with_healing(page, ['input[name="session[username_or_email]"]', 'input[type="text"]'])
        user_in.fill(username)
    except Exception:
        pass

    try:
        pass_in = find_locator_with_healing(page, ['input[type="password"]'])
        pass_in.fill(password)
    except Exception:
        pass

    # Try to click a login button, fallback to Enter
    try:
        btn = find_locator_with_healing(page, ['div[role="button"][data-testid="LoginForm_Login_Button"]', 'button[type="submit"]', 'text=Log in'])
        btn.click()
    except Exception:
        page.keyboard.press('Enter')

    page.wait_for_load_state('networkidle', timeout=10000)
    assert "login" not in page.url
