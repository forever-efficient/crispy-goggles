"""Small helper: try multiple selectors and return the first visible
Playwright locator.

This module is intentionally tiny and written to be resilient to
detached/stale elements and selector parsing errors. Tests rely on this
helper during the migration away from Behave+Selenium.
"""

from collections.abc import Iterable
from typing import Any


def find_locator_with_healing(page: Any, selectors: Iterable[str]) -> Any:
    """Try each selector and return the first visible locator.

    Args:
        page: Playwright page-like object with `locator` method.
        selectors: Iterable of selector strings to try in order.

    Returns:
        The first visible Playwright Locator (typed as ``Any`` here to keep
        mypy/ruff happy without adding Playwright as a typed dependency).

    Raises:
        RuntimeError: if none of the selectors matched or were visible.

    """
    last_ex = None
    for sel in selectors:
        try:
            loc = page.locator(sel)
        except Exception as exc:  # selector parsing/lookup failed
            last_ex = exc
            continue

        try:
            # Use count() + is_visible() to reduce false negatives
            if loc.count() and loc.first.is_visible():
                return loc.first
        except Exception as exc:
            # element may detach / be stale — record and try next selector
            last_ex = exc
            continue

    raise RuntimeError("None of the selectors matched or were visible.") from last_ex
