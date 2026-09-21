"""
Input-permission detection.

pyautogui does not raise when the OS refuses synthetic input — it silently
does nothing. On macOS that turns a missing Accessibility grant into the worst
possible failure: the phone connects, every command returns ok, and the cursor
never moves. This module detects the condition so the server and the UI can
say so plainly instead of pretending to work.
"""

import os
import platform
import subprocess
import sys

SYSTEM = platform.system()


def _macos_executable() -> str:
    """
    The binary macOS actually attributes the Accessibility grant to.

    A venv's bin/python is a symlink; TCC follows it to the real interpreter,
    so that resolved path is what has to be added in System Settings.
    """
    return os.path.realpath(getattr(sys, "_base_executable", None) or sys.executable)


def _macos_trusted() -> bool | None:
    """
    Ask macOS whether this process may post synthetic events.

    Uses ctypes rather than pyobjc: AXIsProcessTrusted is not exposed by every
    pyobjc build, and this needs no extra dependency. Returns None if the check
    itself could not run, which is different from a definite "no".

    There is deliberately no prompting variant. AXIsProcessTrustedWithOptions
    takes a CFDictionary, and building one through ctypes segfaulted the
    interpreter — not something worth risking in the startup path for a
    convenience dialog, especially as the dialog would name the launching app
    rather than this one (see _responsible_app).
    """
    import ctypes
    import ctypes.util

    try:
        path = ctypes.util.find_library("ApplicationServices")
        if not path:
            return None
        lib = ctypes.cdll.LoadLibrary(path)
        lib.AXIsProcessTrusted.restype = ctypes.c_bool
        lib.AXIsProcessTrusted.argtypes = []
        return bool(lib.AXIsProcessTrusted())
    except Exception:
        return None


def _responsible_app() -> str | None:
    """
    Name the .app that macOS holds responsible for this process.

    Accessibility is granted to the *responsible* process, not the binary that
    calls the API. For a server started from a shell that is the terminal
    emulator, so telling someone to enable the Python binary sends them to the
    wrong switch. Walk up the tree and find the owning bundle.
    """
    try:
        import psutil
    except Exception:
        return None
    try:
        proc = psutil.Process()
        for _ in range(12):
            proc = proc.parent()
            if proc is None:
                return None
            exe = proc.exe() or ""
            if ".app/Contents/MacOS/" in exe:
                return exe.split(".app/Contents/MacOS/")[0].split("/")[-1] + ".app"
    except Exception:
        return None
    return None


def _linux_display() -> tuple[bool, str | None]:
    """pyautogui drives X11; a pure Wayland session has no way in."""
    if os.environ.get("DISPLAY"):
        return True, None
    if os.environ.get("WAYLAND_DISPLAY"):
        return False, (
            "Running under Wayland, which does not allow synthetic input. "
            "Log in to an Xorg session, or run with XWayland available."
        )
    return False, "No DISPLAY is set — the server cannot reach a graphical session."


def input_status() -> dict:
    """
    Report whether this process can actually drive the mouse and keyboard.

    Returns {ok, reason, fix, binary, platform}. `ok` is True when input should
    work, False when it definitely won't, and True with a `reason` when the
    check could not be made (better to let the user try than to cry wolf).
    """
    status = {
        "ok": True,
        "reason": None,
        "fix": None,
        "binary": sys.executable,
        "platform": SYSTEM,
    }

    if SYSTEM == "Darwin":
        binary = _macos_executable()
        status["binary"] = binary
        trusted = _macos_trusted()
        if trusted is False:
            app = _responsible_app()
            status["ok"] = False
            status["responsible_app"] = app
            status["reason"] = (
                "macOS is blocking synthetic input: this process is not "
                "trusted for Accessibility."
            )
            target = (
                f"{app}  (the app you started the server from)"
                if app
                else "the app you started the server from (Terminal, iTerm, …)"
            )
            status["fix"] = (
                "System Settings → Privacy & Security → Accessibility,\n"
                "then switch ON:\n"
                f"    {target}\n"
                "macOS grants this to the launching app, not to Python. If you\n"
                "start the server some other way, add this binary instead:\n"
                f"    {binary}\n"
                "Then quit the server and start it again — the permission is\n"
                "only picked up by a fresh process."
            )
        elif trusted is None:
            status["reason"] = "Could not verify Accessibility permission."

    elif SYSTEM == "Linux":
        ok, reason = _linux_display()
        if not ok:
            status["ok"] = False
            status["reason"] = reason
            status["fix"] = "Start the server from inside a graphical X11 session."

    return status


def probe_input() -> bool | None:
    """
    Empirically check that a cursor move actually lands.

    The permission API can disagree with reality (a stale TCC grant for a
    replaced binary, for instance), so this nudges the cursor by one pixel and
    puts it straight back. Returns None if the probe could not run.
    """
    try:
        import pyautogui

        pyautogui.FAILSAFE = False
        before = pyautogui.position()
        pyautogui.moveRel(1, 1, duration=0)
        after = pyautogui.position()
        pyautogui.moveTo(before.x, before.y, duration=0)
        return (after.x, after.y) != (before.x, before.y)
    except Exception:
        return None
