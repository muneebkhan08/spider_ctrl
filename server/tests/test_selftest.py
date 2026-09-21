"""
Smoke tests for selftest.py.

A diagnostic that crashes is worse than no diagnostic — it is the thing people
reach for when something is already wrong. These checks only assert that it
runs and reports, not what the verdict is, since that depends on the machine.
"""

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))


@pytest.fixture
def selftest():
    spec = importlib.util.spec_from_file_location("selftest", SERVER_DIR / "selftest.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.results.clear()
    return mod


def test_runs_to_completion_and_returns_an_exit_code(selftest):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = selftest.main()
    assert code in (0, 1)
    assert buf.getvalue().strip()


def test_every_check_reports_something(selftest):
    with redirect_stdout(io.StringIO()):
        selftest.main()
    names = [n for n, _, _ in selftest.results]
    for expected in (
        "Python 3.9+", "Dependencies", "Frontend build",
        "Pairing token", "Mouse control", "Keyboard control",
        "Screen capture", "LAN address", "Port 8765",
    ):
        assert expected in names, f"{expected} was not reported"


def test_no_check_is_left_in_an_unknown_state(selftest):
    with redirect_stdout(io.StringIO()):
        selftest.main()
    allowed = {selftest.PASS, selftest.FAIL, selftest.WARN}
    assert all(state in allowed for _, state, _ in selftest.results)


def test_a_failure_always_carries_a_detail(selftest):
    """A bare FAIL tells the user nothing about what to do next."""
    with redirect_stdout(io.StringIO()):
        selftest.main()
    for name, state, detail in selftest.results:
        if state == selftest.FAIL:
            assert detail.strip(), f"{name} failed without saying why"


def test_individual_checks_do_not_raise(selftest):
    for fn in (
        selftest.check_python, selftest.check_packages, selftest.check_frontend,
        selftest.check_pairing, selftest.check_input, selftest.check_screen,
        selftest.check_controllers, selftest.check_network,
    ):
        with redirect_stdout(io.StringIO()):
            fn()
