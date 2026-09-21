"""
Server-level authentication tests.

test_pairing.py covers the pairing primitives in isolation; this file drives
the real FastAPI app, so it checks the wiring: that the routes actually apply
the policy, and that a rotation reaches devices that are already connected.

Needs the full runtime (requirements.txt), because importing server.py pulls
in the controllers.

    venv/bin/python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

import server  # noqa: E402
from utils import pairing  # noqa: E402

REMOTE = "https://spider-ctrl.vercel.app"


class _FakeClient:
    def __init__(self, host):
        self.host = host


class _FakeRequest:
    """Just enough of a Request for the loopback guard."""
    def __init__(self, host):
        self.client = _FakeClient(host) if host else None


def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(pairing, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(pairing, "TOKEN_FILE", tmp_path / "pairing.json")
    monkeypatch.setattr(pairing, "_token", None)
    monkeypatch.setattr(
        server, "ALLOWED_ORIGINS",
        pairing.local_origins(server.SERVER_PORT, server.LOCAL_IP) + [REMOTE],
    )
    monkeypatch.setattr(server, "REMOTE_ORIGINS", [REMOTE])
    pairing.pair_code.issue()


@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Client with an isolated token file, treated as loopback.

    The pinned Starlette hardcodes the test client's address, so the guard is
    forced here and verified for real in test_loopback_guard below.
    """
    _isolate(tmp_path, monkeypatch)
    monkeypatch.setattr(server, "_loopback", lambda request: True)
    with TestClient(server.app) as c:
        yield c


@pytest.fixture
def remote_app(tmp_path, monkeypatch):
    """Same app, but every caller looks like it came from the LAN."""
    _isolate(tmp_path, monkeypatch)
    monkeypatch.setattr(server, "_loopback", lambda request: False)
    with TestClient(server.app) as c:
        yield c


# ── the loopback guard itself ───────────────────────────────────────────────
@pytest.mark.parametrize("host,expected", [
    ("127.0.0.1", True),
    ("::1", True),
    ("localhost", True),
    ("192.168.1.99", False),
    ("10.0.0.5", False),
    ("", False),
    (None, False),
])
def test_loopback_guard(host, expected):
    assert server._loopback(_FakeRequest(host)) is expected


# ── /pair exposure ──────────────────────────────────────────────────────────
def test_pair_served_to_loopback(app):
    body = app.get("/pair").json()
    assert len(body["token"]) >= 32
    assert body["qr"].startswith("data:image/svg+xml;base64,")


def test_pair_refused_to_lan_callers(remote_app):
    r = remote_app.get("/pair")
    assert r.status_code == 403
    assert "token" not in r.text


@pytest.mark.parametrize("origin,expected", [(REMOTE, 200), ("https://evil.com", 403)])
def test_pair_origin_allowlist(app, origin, expected):
    assert app.get("/pair", headers={"Origin": origin}).status_code == expected


def test_hostile_origin_never_sees_the_token(app):
    assert "token" not in app.get("/pair", headers={"Origin": "https://evil.com"}).text


def test_private_network_access_only_for_allowlisted(app):
    hdrs = {
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Private-Network": "true",
    }
    good = app.options("/pair", headers={**hdrs, "Origin": REMOTE})
    bad = app.options("/pair", headers={**hdrs, "Origin": "https://evil.com"})
    assert good.headers.get("access-control-allow-private-network") == "true"
    assert bad.headers.get("access-control-allow-private-network") is None


# ── code exchange ───────────────────────────────────────────────────────────
def test_claim_exchanges_code_for_token(app):
    token = app.get("/pair").json()["token"]
    code = app.get("/pair").json()["code"]
    assert app.post("/pair/claim", json={"code": code}).json()["token"] == token
    # single use
    assert app.post("/pair/claim", json={"code": code}).status_code == 403


def test_claim_rejects_wrong_code_and_junk(app):
    assert app.post("/pair/claim", json={"code": "ZZZ-ZZZ"}).status_code == 403
    assert app.post("/pair/claim", content=b"not json").status_code == 400


# ── WebSocket ───────────────────────────────────────────────────────────────
def ws_open(client, qs, headers=None):
    """True if the socket stays open long enough to answer."""
    try:
        with client.websocket_connect("/ws" + qs, headers=headers or {}) as ws:
            ws.send_json({"action": "terminal_cwd", "id": "t"})
            ws.receive_json()
        return True
    except Exception:
        return False


def test_ws_requires_a_token(app):
    assert not ws_open(app, "")
    assert not ws_open(app, "?t=")
    assert not ws_open(app, "?t=wrong")


def test_ws_accepts_the_real_token(app):
    assert ws_open(app, "?t=" + app.get("/pair").json()["token"])


def test_ws_rejects_hostile_origins(app):
    token = app.get("/pair").json()["token"]
    assert ws_open(app, f"?t={token}", {"Origin": f"http://{server.LOCAL_IP}:8765"})
    assert not ws_open(app, f"?t={token}", {"Origin": "https://evil.com"})
    # An attacker's dev server on this very machine is still a different origin.
    assert not ws_open(app, f"?t={token}", {"Origin": "http://127.0.0.1:3000"})


def test_unpaired_socket_cannot_run_a_command(app):
    """The socket is accepted before the check, so prove nothing executes."""
    executed = False
    try:
        with app.websocket_connect("/ws") as ws:
            ws.send_json({
                "action": "terminal_execute",
                "payload": {"command": "echo pwned"},
                "id": "x",
            })
            executed = "pwned" in str(ws.receive_json())
    except Exception:
        executed = False
    assert not executed


# ── rotation ────────────────────────────────────────────────────────────────
def test_rotate_invalidates_the_old_token(app):
    old = app.get("/pair").json()["token"]
    assert app.post("/pair/rotate").status_code == 200
    new = app.get("/pair").json()["token"]
    assert new != old
    assert not ws_open(app, "?t=" + old)
    assert ws_open(app, "?t=" + new)


def test_rotate_is_loopback_only(remote_app):
    assert remote_app.post("/pair/rotate").status_code == 403


def test_rotate_revokes_a_live_socket(app):
    """
    The token is only checked at handshake time, so a rotation has to actively
    kick sockets that are already open — otherwise rotating to get rid of a
    lost device would leave that device connected.
    """
    token = app.get("/pair").json()["token"]
    with app.websocket_connect(f"/ws?t={token}") as ws:
        ws.send_json({"action": "terminal_cwd", "id": "a"})
        ws.receive_json()                     # confirmed live

        assert app.post("/pair/rotate").json()["disconnected"] == 1

        # The next read must surface the close rather than more data.
        with pytest.raises(Exception):
            ws.send_json({"action": "terminal_cwd", "id": "b"})
            for _ in range(3):
                ws.receive_json()


def test_registry_does_not_leak_closed_sockets(app):
    token = app.get("/pair").json()["token"]
    for _ in range(3):
        with app.websocket_connect(f"/ws?t={token}") as ws:
            ws.send_json({"action": "terminal_cwd", "id": "c"})
            ws.receive_json()
    assert app.post("/pair/rotate").json()["disconnected"] == 0
