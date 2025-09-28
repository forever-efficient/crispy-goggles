import contextlib
from pathlib import Path

import pytest
from _pytest.runner import CallInfo
import os
import json
import subprocess
import sys


def _playwright_cache_dirs() -> list:
    """Return candidate Playwright cache directories to check for installed browsers."""
    env = os.getenv("PLAYWRIGHT_BROWSERS_PATH")
    if env:
        return [Path(env)]
    return [Path(os.path.expanduser("~")) / ".cache" / "ms-playwright", Path(os.path.expanduser("~")) / ".cache" / "playwright"]


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
    # Only enforce in CI environments
    if not (os.getenv("CI") or os.getenv("GITHUB_ACTIONS") or os.getenv("GITLAB_CI")):
        return

    # Per project policy: never run Playwright/browser tests in CI. Mark any
    # test that requests the pytest-playwright 'page' fixture as skipped so the
    # CI test run cannot launch browsers or trigger installers.
    skip_reason = "Playwright/browser tests are disabled in CI (local-only)"
    for item in items:
        if "page" in getattr(item, "fixturenames", []):
            item.add_marker(pytest.mark.skip(reason=skip_reason))



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
    """Fail early if TEST_USE_AUTH_STATE is set but auth_state.json missing/invalid.

    This prevents running tests that expect an authenticated state when none is
    available.
    """
    use_auth = os.getenv("TEST_USE_AUTH_STATE")
    if not use_auth or use_auth == "0":
        return

    auth_path = os.path.join(os.getcwd(), "auth_state.json")
    if not os.path.exists(auth_path):
        # If running in CI, fail fast. Otherwise try to run the interactive
        # helper to create the auth_state locally.
        ci_indicators = [
            os.getenv("CI"),
            os.getenv("GITHUB_ACTIONS"),
            os.getenv("GITLAB_CI"),
        ]
        if any(ci_indicators):
            pytest.fail("TEST_USE_AUTH_STATE is set but auth_state.json not found in CI")

        # Attempt to run the local interactive helper script to obtain auth state.
        helper = Path(os.getcwd()) / "scripts" / "ensure_auth_state.py"
        if helper.exists():
            try:
                print("auth_state.json not found — launching interactive helper to record it.")
                # Use the current Python executable from the environment
                python_exe = os.getenv("PYTHON", "python")
                subprocess.check_call([python_exe, str(helper), "--output", auth_path])
            except Exception as e:
                pytest.fail(f"Failed to run interactive ensure_auth_state helper: {e}")

        if not os.path.exists(auth_path):
            pytest.fail("TEST_USE_AUTH_STATE is set but auth_state.json not found after interactive attempt")

    try:
        with open(auth_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        pytest.fail("Failed to read/parse auth_state.json")

    cookies = data.get("cookies", []) if isinstance(data, dict) else []
    if not any(c.get("name") == "auth_token" for c in cookies):
        pytest.fail("auth_state.json does not contain expected auth_token cookie")
