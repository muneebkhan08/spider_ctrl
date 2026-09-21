"""
Tests for input-permission detection.

The point of this module is that pyautogui fails *silently* when the OS
refuses synthetic input, so these tests care most about two things: the report
is well-formed on every platform, and the check never takes the server down
with it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import permissions  # noqa: E402


# ── contract ────────────────────────────────────────────────────────────────
def test_status_has_the_expected_shape():
    s = permissions.input_status()
    assert set(["ok", "reason", "fix", "binary", "platform"]) <= set(s)
    assert isinstance(s["ok"], bool)
    assert isinstance(s["binary"], str) and s["binary"]


def test_status_is_json_serialisable():
    """It is sent over the control channel, so it has to survive json.dumps."""
    import json
    json.dumps(permissions.input_status())


def test_status_never_raises(monkeypatch):
    """
    Regression guard.

    An earlier version built a CFDictionary through ctypes to show the macOS
    permission dialog and segfaulted the interpreter. This runs in the server's
    startup path, so a crash here takes the whole server with it.
    """
    for system in ("Darwin", "Linux", "Windows", "SomethingElse"):
        monkeypatch.setattr(permissions, "SYSTEM", system)
        s = permissions.input_status()
        assert isinstance(s["ok"], bool)


def test_no_prompting_api_is_reachable():
    """
    The prompting variant is deliberately absent — see _macos_trusted.
    If someone reintroduces it, this fails and they have to read why.
    """
    assert not hasattr(permissions, "_macos_trusted_with_prompt")
    import inspect
    sig = inspect.signature(permissions.input_status)
    assert "prompt" not in sig.parameters


# ── a blocked host must be reported as blocked ──────────────────────────────
def test_macos_untrusted_is_reported_with_a_fix(monkeypatch):
    monkeypatch.setattr(permissions, "SYSTEM", "Darwin")
    monkeypatch.setattr(permissions, "_macos_trusted", lambda: False)
    monkeypatch.setattr(permissions, "_responsible_app", lambda: "Terminal.app")
    s = permissions.input_status()
    assert s["ok"] is False
    assert "Accessibility" in s["reason"]
    # The grant goes to the launching app, so that must be what we name first.
    assert "Terminal.app" in s["fix"]
    assert "restart" in s["fix"].lower() or "start it again" in s["fix"].lower()


def test_macos_trusted_is_reported_ok(monkeypatch):
    monkeypatch.setattr(permissions, "SYSTEM", "Darwin")
    monkeypatch.setattr(permissions, "_macos_trusted", lambda: True)
    s = permissions.input_status()
    assert s["ok"] is True and s["fix"] is None


def test_macos_unknown_does_not_cry_wolf(monkeypatch):
    """An unverifiable check must not claim input is broken."""
    monkeypatch.setattr(permissions, "SYSTEM", "Darwin")
    monkeypatch.setattr(permissions, "_macos_trusted", lambda: None)
    s = permissions.input_status()
    assert s["ok"] is True
    assert s["reason"] is not None


def test_macos_fix_falls_back_when_the_app_is_unknown(monkeypatch):
    monkeypatch.setattr(permissions, "SYSTEM", "Darwin")
    monkeypatch.setattr(permissions, "_macos_trusted", lambda: False)
    monkeypatch.setattr(permissions, "_responsible_app", lambda: None)
    s = permissions.input_status()
    assert s["ok"] is False and "Terminal" in s["fix"]


# ── Linux display detection ─────────────────────────────────────────────────
@pytest.mark.parametrize("env,ok,needle", [
    ({"DISPLAY": ":0"}, True, None),
    ({"WAYLAND_DISPLAY": "wayland-0"}, False, "Wayland"),
    ({}, False, "DISPLAY"),
])
def test_linux_display(monkeypatch, env, ok, needle):
    monkeypatch.setattr(permissions, "SYSTEM", "Linux")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    s = permissions.input_status()
    assert s["ok"] is ok
    if needle:
        assert needle in s["reason"]


def test_windows_is_assumed_workable(monkeypatch):
    monkeypatch.setattr(permissions, "SYSTEM", "Windows")
    assert permissions.input_status()["ok"] is True


# ── executable resolution ───────────────────────────────────────────────────
def test_macos_executable_is_a_real_path():
    import os
    path = permissions._macos_executable()
    assert os.path.isabs(path)
    # A venv's bin/python is a symlink; TCC follows it, so we must too.
    assert path == os.path.realpath(path)


# ── empirical probe ─────────────────────────────────────────────────────────
def test_probe_returns_a_tristate():
    assert permissions.probe_input() in (True, False, None)
