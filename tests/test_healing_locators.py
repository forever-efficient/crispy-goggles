import pytest

from types import SimpleNamespace

from utils.healing_locators import find_element_with_healing


class DummyElement:
    def __init__(self, visible=False):
        self._visible = visible

    def count(self):
        return 1 if self._visible else 0

    @property
    def first(self):
        return self

    def is_visible(self):
        return self._visible


class DummyPage:
    def __init__(self, mapping):
        # mapping: selector -> DummyElement
        self._mapping = mapping

    def locator(self, selector):
        if selector not in self._mapping:
            # return an element that is never visible
            return DummyElement(visible=False)
        return self._mapping[selector]


def test_find_element_with_healing_success():
    page = DummyPage({'#ok': DummyElement(visible=True)})
    loc = find_element_with_healing(page, ['#missing', '#ok'], timeout=0.5)
    assert loc.is_visible()


def test_find_element_with_healing_failure():
    page = DummyPage({})
    with pytest.raises(RuntimeError):
        find_element_with_healing(page, ['#nope1', '#nope2'], timeout=0.2)
