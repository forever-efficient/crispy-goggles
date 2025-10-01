import contextlib
from pathlib import Path

import pytest
from _pytest.runner import CallInfo
import os
import json


def _playwright_cache_dirs() -> list:
    """Return candidate Playwright cache directories to check for installed browsers."""
    env = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
    if env:
        return [Path(env)]
    return [
        Path(os.path.expanduser("~")) / ".cache" / "ms-playwright",
        Path(os.path.expanduser("~")) / ".cache" / "playwright",
    ]


def _playwright_browsers_present() -> bool:
    try:
        for d in _playwright_cache_dirs():
            if d.exists() and any(d.iterdir()):
                return True
    except Exception:
        pass
    return False


def pytest_collection_modifyitems(config, items):
    """Skip tests that require Playwright when running in CI without browsers.

    This prevents the test harness from attempting to launch browsers in CI
    when maintainers have opted out of automatic browser installation.
    """
    # Mark tests that request the pytest-playwright 'page' fixture with a
    # marker indicating they are local-only. We no longer gate this on CI
    # environment variables; tests themselves decide to skip based on
    # availability of local artifacts (like auth_state.json).
    for item in items:
        if "page" in getattr(item, "fixturenames", []):
            item.add_marker(pytest.mark.local)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call: CallInfo):
    # run all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # only act on the actual test call
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            Path("artifacts").mkdir(parents=True, exist_ok=True)
            with contextlib.suppress(Exception):
                page.screenshot(path="artifacts/failure.png")
            with contextlib.suppress(Exception):
                with open("artifacts/failure.html", "w", encoding="utf-8") as f:
                    f.write(page.content())


@pytest.fixture(autouse=True)
def trace_on_failure(request):
    # Autouse fixture that starts Playwright tracing only when a real 'page'
    # fixture is present for the test. Important: do NOT request 'page' here
    # to avoid forcing Playwright initialization in CI.
    page = None
    try:
        page = request.node.funcargs.get("page")
    except Exception:
        page = None

    if page:
        with contextlib.suppress(Exception):
            page.context.tracing.start(snapshots=True, screenshots=True)

    yield

    # after the test finishes, only stop/save tracing if a page was used
    report = request.node.rep_call if hasattr(request.node, "rep_call") else None
    if page and report is not None and report.failed:
        Path("artifacts").mkdir(parents=True, exist_ok=True)
        trace_path = "artifacts/test_trace.zip"
        with contextlib.suppress(Exception):
            page.context.tracing.stop(path=trace_path)
    elif page:
        with contextlib.suppress(Exception):
            page.context.tracing.stop()


@pytest.fixture(autouse=True)
def require_auth_state():
    """If an `auth_state.json` exists, validate it contains an auth_token cookie.

    Historically this fixture created or enforced auth state via environment
    variables; we now simply check the file if it exists. Tests that require an
    authenticated context should explicitly skip when the file is absent.
    """
    auth_path = os.path.join(os.getcwd(), "auth_state.json")
    if not os.path.exists(auth_path):
        return

    try:
        with open(auth_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        pytest.fail("Failed to read/parse auth_state.json")

    cookies = data.get("cookies", []) if isinstance(data, dict) else []
    if not any(c.get("name") == "auth_token" for c in cookies):
        pytest.fail("auth_state.json does not contain expected auth_token cookie")
