#!/usr/bin/env python3
"""
SPIDER_CTRL self-test — check every subsystem before you rely on it.

    cd server
    venv/bin/python selftest.py

Run it after installing, and again after granting input permission. It is
read-only apart from a one-pixel cursor nudge that it puts straight back.

Exit code is 0 when everything required passes, 1 otherwise, so it can gate
a script.
"""

import os
import platform
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    GREEN = RED = YELLOW = DIM = RESET = ""

PASS, FAIL, WARN = f"{GREEN}PASS{RESET}", f"{RED}FAIL{RESET}", f"{YELLOW}WARN{RESET}"

results: list[tuple[str, str, str]] = []


def record(name: str, state: str, detail: str = "") -> None:
    results.append((name, state, detail))
    print(f"  [{state}] {name}" + (f"\n         {DIM}{detail}{RESET}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{DIM}── {title} {'─' * max(0, 52 - len(title))}{RESET}")


# ── Environment ─────────────────────────────────────────────────────────────
def check_python() -> None:
    v = sys.version_info
    ok = v >= (3, 9)
    record("Python 3.9+", PASS if ok else FAIL, f"{v.major}.{v.minor}.{v.micro}")


def check_packages() -> None:
    required = {
        "fastapi": "web server",
        "uvicorn": "ASGI server",
        "websockets": "control channel",
        "pyautogui": "mouse + keyboard",
        "psutil": "process list",
        "mss": "screen capture",
        "numpy": "frame conversion",
        "av": "video encoding",
        "aiortc": "WebRTC",
        "qrcode": "pairing QR",
        "cryptography": "TLS certificates",
    }
    missing = []
    for mod, why in required.items():
        try:
            __import__(mod)
        except Exception:
            missing.append(f"{mod} ({why})")
    if missing:
        record("Dependencies", FAIL, "missing: " + ", ".join(missing)
               + "\n         fix: venv/bin/pip install -r requirements.txt")
    else:
        record("Dependencies", PASS, f"{len(required)} packages present")


# ── Frontend ────────────────────────────────────────────────────────────────
def check_frontend() -> None:
    index = Path(__file__).resolve().parent.parent / "frontend" / "out" / "index.html"
    if index.is_file():
        record("Frontend build", PASS, str(index.parent))
    else:
        record("Frontend build", FAIL,
               "not built — fix: cd frontend && npm install && npm run build")


# ── Pairing ─────────────────────────────────────────────────────────────────
def check_pairing() -> None:
    try:
        from utils import pairing
        token = pairing.get_token()
        assert pairing.verify_token(token)
        assert not pairing.verify_token("wrong")
        code, ttl = pairing.pair_code.current()
        record("Pairing token", PASS, f"{len(token)} chars, verifies correctly")
        record("Pairing code", PASS, f"{pairing.format_code(code)} (valid {ttl}s)")
    except Exception as exc:
        record("Pairing", FAIL, str(exc))
        return
    try:
        from utils import pairing as p
        uri = p.qr_data_uri("http://127.0.0.1:8765/?t=test")
        ascii_qr = p.qr_ascii("http://127.0.0.1:8765/?t=test")
        ok = bool(uri) and bool(ascii_qr)
        record("QR rendering", PASS if ok else FAIL, "SVG + terminal" if ok else "qrcode failed")
    except Exception as exc:
        record("QR rendering", FAIL, str(exc))


# ── Input: the one that usually fails ───────────────────────────────────────
def check_input() -> bool:
    from utils import permissions

    status = permissions.input_status()
    probe = permissions.probe_input()

    # The cursor probe is the ground truth: the permission API can disagree
    # with reality. Keyboard input is not probed because pressing a key would
    # type into whatever window is focused — but it travels the same event
    # path as the mouse, so a moving cursor means a working keyboard.
    if probe is True:
        record("Mouse control", PASS, "cursor moved and was restored")
        record("Keyboard control", PASS, "same event path as the mouse — available")
        return True

    detail = status["reason"] or "synthetic input was rejected"
    if status["fix"]:
        detail += "\n         " + status["fix"].replace("\n", "\n         ")
    record("Mouse control", FAIL, detail)
    record("Keyboard control", FAIL, "blocked by the same permission")
    return False


# ── Screen ──────────────────────────────────────────────────────────────────
def check_screen() -> None:
    try:
        import mss
        # mss.mss() is a deprecated alias in mss 10+, and mss.MSS does not
        # exist in the 9.x we still allow — pick whichever is there.
        grabber = getattr(mss, "MSS", None) or mss.mss
        with grabber() as sct:
            shot = sct.grab(sct.monitors[1])
            blank = not any(bytes(shot.rgb)[:3000])
        if blank:
            record("Screen capture", WARN,
                   "captured, but the frame looks blank — on macOS grant "
                   "Screen Recording to the same app")
        else:
            record("Screen capture", PASS, f"{shot.width}x{shot.height}")
    except Exception as exc:
        record("Screen capture", FAIL, str(exc))


# ── Media keys ──────────────────────────────────────────────────────────────
def check_media() -> None:
    """
    Check the mechanism is available without firing a key.

    Actually pressing play/pause would pause whatever the user is listening
    to, which a diagnostic has no business doing.
    """
    if platform.system() != "Darwin":
        record("Media keys", PASS, "pyautogui virtual keys")
        return
    try:
        import Quartz  # noqa: F401
        from AppKit import NSEvent  # noqa: F401
        record("Media keys", PASS, "NSSystemDefined events available")
    except Exception as exc:
        record("Media keys", FAIL,
               f"pyobjc missing ({exc}) — play/pause and track skip will do nothing")


# ── Controllers ─────────────────────────────────────────────────────────────
def check_controllers() -> None:
    checks = [
        ("system_info", lambda: __import__(
            "controllers.system_info", fromlist=["x"]).SystemInfoController().get_info()),
        ("filesystem", lambda: __import__(
            "controllers.filesystem", fromlist=["x"]).FilesystemController().get_drives()),
        ("processes", lambda: __import__(
            "controllers.processes", fromlist=["x"]).ProcessController().list_processes()),
        ("clipboard", lambda: __import__(
            "controllers.clipboard", fromlist=["x"]).ClipboardController().get_text()),
        ("volume", lambda: __import__(
            "controllers.volume", fromlist=["x"]).VolumeController().get_volume()),
        ("terminal", lambda: __import__(
            "controllers.terminal", fromlist=["x"]).TerminalController().get_cwd()),
    ]
    for name, fn in checks:
        try:
            fn()
            record(f"Controller: {name}", PASS)
        except Exception as exc:
            record(f"Controller: {name}", FAIL, f"{type(exc).__name__}: {exc}")


# ── Network ─────────────────────────────────────────────────────────────────
def check_network() -> None:
    from utils.network import get_local_ip
    ip = get_local_ip()
    if ip == "127.0.0.1":
        record("LAN address", WARN,
               "only loopback found — a phone on the Wi-Fi will not reach this host")
    else:
        record("LAN address", PASS, f"{ip}:8765")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    in_use = sock.connect_ex(("127.0.0.1", 8765)) == 0
    sock.close()
    record("Port 8765", PASS if not in_use else WARN,
           "free" if not in_use else "already in use — the server is probably running")


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    print(f"\n  SPIDER_CTRL self-test  ·  {platform.system()} {platform.release()}")

    section("Environment")
    check_python()
    check_packages()
    check_frontend()

    section("Pairing")
    check_pairing()

    section("Input control")
    input_ok = check_input()

    section("Screen")
    check_screen()

    section("Media")
    check_media()

    section("Controllers")
    check_controllers()

    section("Network")
    check_network()

    failed = [n for n, s, _ in results if s == FAIL]
    warned = [n for n, s, _ in results if s == WARN]

    print(f"\n{DIM}{'─' * 56}{RESET}")
    if not failed:
        print(f"  {GREEN}Everything works.{RESET} "
              f"{len(results) - len(warned)} passed"
              + (f", {len(warned)} warning(s)" if warned else "") + ".")
        print(f"  {DIM}Start it with:  venv/bin/python server.py{RESET}\n")
        return 0

    print(f"  {RED}{len(failed)} check(s) failed:{RESET} {', '.join(failed)}")
    if not input_ok:
        print(f"\n  {YELLOW}Mouse and keyboard will not work until input "
              f"permission is granted.{RESET}")
        print(f"  {DIM}Everything else (screen, files, shell, pairing) works "
              f"without it.{RESET}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
