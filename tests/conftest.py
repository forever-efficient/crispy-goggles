import os
import pytest
from _pytest.runner import CallInfo


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call: CallInfo):
    # run all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # only act on the actual test call
    if rep.when == 'call' and rep.failed:
        page = item.funcargs.get('page')
        if page:
            os.makedirs('artifacts', exist_ok=True)
            try:
                page.screenshot(path='artifacts/failure.png')
            except Exception:
                pass
            try:
                with open('artifacts/failure.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
            except Exception:
                pass
