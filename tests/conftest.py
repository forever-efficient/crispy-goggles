import contextlib
from pathlib import Path

import pytest
from _pytest.runner import CallInfo
import os
import json
import subprocess


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
def trace_on_failure(page, request):
    # start tracing for each test; stop and save only on failure to avoid large outputs
    # Playwright trace API available via page.context.tracing
    with contextlib.suppress(Exception):
        page.context.tracing.start(snapshots=True, screenshots=True)
    yield
    # after the test finishes
    report = request.node.rep_call if hasattr(request.node, "rep_call") else None
    if report is not None and report.failed:
        Path("artifacts").mkdir(parents=True, exist_ok=True)
        trace_path = "artifacts/test_trace.zip"
        with contextlib.suppress(Exception):
            page.context.tracing.stop(path=trace_path)
    else:
        # stop tracing without saving if test passed
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
