"""
Tests for the pairing layer.

This is the code that decides who may drive the machine, so the negative
cases matter more than the happy path: a regression here is a stranger on the
Wi-Fi getting a shell, not a cosmetic bug.

Run from the server directory:

    venv/bin/python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import pairing  # noqa: E402

PORT = 8765
REMOTE = "https://spider-ctrl.vercel.app"


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Keep every test off the real token file."""
    monkeypatch.setattr(pairing, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(pairing, "TOKEN_FILE", tmp_path / "pairing.json")
    monkeypatch.setattr(pairing, "_token", None)
    pairing.pair_code.issue()
    yield


# ── Token ───────────────────────────────────────────────────────────────────
def test_token_is_long_and_stable():
    token = pairing.get_token()
    assert len(token) >= 32
    assert pairing.get_token() == token


def test_token_persists_to_disk():
    token = pairing.get_token()
    pairing._token = None  # force a reload from the file
    assert pairing.get_token() == token


def test_verify_rejects_wrong_and_empty():
    pairing.get_token()
    assert not pairing.verify_token("wrong")
    assert not pairing.verify_token("")
    assert not pairing.verify_token(None)


def test_rotate_invalidates_the_old_token():
    old = pairing.get_token()
    new = pairing.rotate_token()
    assert new != old
    assert pairing.verify_token(new)
    assert not pairing.verify_token(old)


# ── Pairing code ────────────────────────────────────────────────────────────
def test_code_avoids_ambiguous_characters():
    code = pairing.pair_code.issue()
    assert len(code) == pairing.CODE_LENGTH
    assert not set(code) & set("ILOU01")


def test_code_accepts_dashes_and_lowercase():
    code = pairing.pair_code.issue()
    assert pairing.pair_code.claim(pairing.format_code(code).lower())


def test_code_is_single_use():
    code = pairing.pair_code.issue()
    assert pairing.pair_code.claim(code)
    assert not pairing.pair_code.claim(code)


def test_code_burns_after_max_attempts():
    code = pairing.pair_code.issue()
    wrong = "".join("Z" if c != "Z" else "Y" for c in code)
    for _ in range(pairing.CODE_MAX_ATTEMPTS):
        assert not pairing.pair_code.claim(wrong)
    # Even the correct code must now fail — otherwise the attempt cap would
    # only slow an attacker down rather than stop them.
    assert not pairing.pair_code.claim(code)


def test_expired_code_is_refused(monkeypatch):
    code = pairing.pair_code.issue()
    monkeypatch.setattr(
        pairing.time, "time", lambda: pairing.pair_code.expires_at + 1
    )
    assert not pairing.pair_code.claim(code)


# ── Origin policy ───────────────────────────────────────────────────────────
def allowed(origin):
    return pairing.is_origin_allowed(origin, PORT, {REMOTE})


@pytest.mark.parametrize(
    "origin",
    [
        None,                          # non-browser client; token still required
        "http://192.168.1.42:8765",    # phone on the LAN
        "http://localhost:8765",
        "https://localhost:8765",
        REMOTE,                        # the deployed setup page
    ],
)
def test_origins_that_should_pass(origin):
    assert allowed(origin)


@pytest.mark.parametrize(
    "origin",
    [
        "https://evil.com",
        "http://evil.com",
        "http://evil.com:80",
        "https://evil.com:443",
        f"{REMOTE}.evil.com",          # suffix must not satisfy the allowlist
        "http://127.0.0.1:3000",       # attacker's dev server on this machine
        "file://",
        "null",
    ],
)
def test_origins_that_should_fail(origin):
    assert not allowed(origin)


def test_local_origins_cover_loopback_and_lan():
    origins = pairing.local_origins(PORT, "192.168.1.42")
    assert "http://localhost:8765" in origins
    assert "http://127.0.0.1:8765" in origins
    assert "http://192.168.1.42:8765" in origins


# ── QR ──────────────────────────────────────────────────────────────────────
def test_qr_renders_both_forms():
    pytest.importorskip("qrcode")
    url = "http://192.168.1.42:8765/?t=abc"
    assert len(pairing.qr_ascii(url).splitlines()) > 10
    # A data URI, not raw markup: it is rendered via <img>, where SVG cannot
    # execute script.
    assert pairing.qr_data_uri(url).startswith("data:image/svg+xml;base64,")
