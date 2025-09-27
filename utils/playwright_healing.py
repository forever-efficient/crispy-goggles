from typing import List


def find_locator_with_healing(page, selectors: List[str]):
    """Try each selector and return the first visible locator.

    Keeps caller code concise and centralizes fallback logic.
    """
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() and loc.first.is_visible():
                return loc.first
        except Exception:
            # ignore invalid selectors or errors and continue
            continue
    raise RuntimeError(f"None of the selectors matched or were visible: {selectors}")
