"""Unit tests for the Playwright selector healing helper.

These are lightweight, pure-Python tests using dummy page/element objects so
they can run quickly without a browser.
"""

import pytest

from utils.playwright_healing import find_locator_with_healing


class DummyElement:
    def __init__(self, visible: bool = False) -> None:
        self._visible = visible

    def count(self) -> int:
        return 1 if self._visible else 0

    @property
    def first(self):
        return self

    def is_visible(self) -> bool:
        return self._visible


class DummyPage:
    def __init__(self, mapping: dict) -> None:
        # mapping: selector -> DummyElement
        self._mapping = mapping

    def locator(self, selector: str):
        if selector not in self._mapping:
            # return an element that is never visible
            return DummyElement(visible=False)
        return self._mapping[selector]


def test_find_locator_with_healing_success() -> None:
    page = DummyPage({"#ok": DummyElement(visible=True)})
    loc = find_locator_with_healing(page, ["#missing", "#ok"])
    assert loc.is_visible()


def test_find_locator_with_healing_failure() -> None:
    page = DummyPage({})
    with pytest.raises(RuntimeError):
        find_locator_with_healing(page, ["#nope1", "#nope2"])
