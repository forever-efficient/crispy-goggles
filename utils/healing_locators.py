# Use GitHub Copilot to help write this function.
# Type "def find_element_with_healing" and let it suggest the arguments and logic.

from playwright.sync_api import Page, Locator
import time
from typing import List, Optional


def find_element_with_healing(page: Page, locators: List[str], timeout: float = 5.0) -> Locator:
    """Try each selector in `locators` until one resolves and is visible.

    Args:
        page: Playwright Page from `features/environment.py` (use `context.page`).
        locators: ordered list of selector strings to try.
        timeout: maximum seconds to wait per locator before trying the next.

    Returns:
        A Playwright Locator for the first selector that is visible.

    Raises:
        RuntimeError if none of the locators matched within their timeouts.
    """
    start = time.time()
    last_error: Optional[Exception] = None
    for locator_str in locators:
        try:
            element = page.locator(locator_str)
            # wait up to `timeout` for the element to be attached and visible
            end_time = time.time() + timeout
            while time.time() < end_time:
                try:
                    # Use count() + is_visible() to avoid stale-node false negatives
                    if element.count() > 0 and element.first.is_visible():
                        print(f"Found element using locator: '{locator_str}'")
                        return element.first
                except Exception as e:
                    last_error = e
                time.sleep(0.1)
        except Exception as e:
            last_error = e
            print(f"Locator parse/lookup failed fast: '{locator_str}' -> {e}")
            continue

    total = time.time() - start
    raise RuntimeError(f"All locators failed after {total:.1f}s. Tried: {locators}. Last error: {last_error}")