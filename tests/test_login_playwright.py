import os
import pytest


@pytest.mark.local
def test_login_x_com(page: "playwright.sync_api.Page"):
    """Login to x.com using Playwright and environment credentials.

    This mirrors the previous Behave scenario but uses Playwright's Python API
    and pytest-playwright's `page` fixture.
    """
    username = os.getenv("TEST_LOGIN_USERNAME")
    password = os.getenv("TEST_LOGIN_PASSWORD")
    if not username or not password:
        pytest.skip("TEST_LOGIN_USERNAME/TEST_LOGIN_PASSWORD not set; skipping local test")

    page.goto("https://x.com")

    # Try a few selectors that historically worked
    login_selector_candidates = [
        'a[aria-label="Log in"]',
        'a[href*="/login"]',
        'text=Log in',
    ]

    login_btn = None
    for sel in login_selector_candidates:
        loc = page.locator(sel)
        if loc.count() and loc.first.is_visible():
            login_btn = loc.first
            break

    assert login_btn is not None, "Could not find a Log in button on x.com"
    login_btn.click()

    # Fill username/password using playwight locators
    page.wait_for_timeout(1000)
    if page.locator('input[name="session[username_or_email]"]').count():
        page.fill('input[name="session[username_or_email]"]', username)
    elif page.locator('input[type="text"]').count():
        page.fill('input[type="text"]', username)

    if page.locator('input[type="password"]').count():
        page.fill('input[type="password"]', password)

    # submit
    if page.locator('div[role="button"][data-testid="LoginForm_Login_Button"]').count():
        page.click('div[role="button"][data-testid="LoginForm_Login_Button"]')
    else:
        page.keyboard.press('Enter')

    # Wait a bit and assert we've navigated away from the login page
    page.wait_for_load_state('networkidle', timeout=10000)
    assert "login" not in page.url
