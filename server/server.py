"""
SPIDER_CTRL Server — Main Entry Point
Runs a FastAPI WebSocket server + UDP broadcast for auto-discovery.
Also serves the frontend static files so everything runs from one server.
"""

import asyncio
import json
import logging
import os
import socket
import threading
import time
import platform
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from controllers.mouse import MouseController
from controllers.keyboard import KeyboardController
from controllers.power import PowerController
from controllers.apps import AppController
from controllers.search import SearchController
from controllers.volume import VolumeController
from controllers.media import MediaController
from controllers.clipboard import ClipboardController
from controllers.system_info import SystemInfoController
from controllers.screen import ScreenController
from controllers.terminal import TerminalController
from controllers.processes import ProcessController
from controllers.filesystem import FilesystemController
from utils import pairing
from utils.network import get_local_ip
from utils.ssl_cert import ensure_ssl_certs

# Configure logging for WebRTC
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

# ── Constants ────────────────────────────────────────────────────────────────
SERVER_PORT = 8765
UDP_PORT = 8766
BROADCAST_INTERVAL = 2  # seconds
APP_NAME = "SPIDER_CTRL Server"
PROTOCOL_VERSION = "1.0.0"

# Static frontend produced by `next build` (output: "export")
FRONTEND_DIR = (Path(__file__).parent.parent / "frontend" / "out").resolve()

# TLS opt-in: set SPIDER_CTRL_TLS=1 to serve over HTTPS/WSS
ENABLE_TLS = os.environ.get("SPIDER_CTRL_TLS", "").lower() in ("1", "true", "yes")

# Hosted copies of the UI allowed to talk to this server. The deployed site
# only ever reads /pair over loopback to show a QR code — it never controls
# the machine — but that response carries the pairing token, so the origin
# list has to stay exact. Override with a comma-separated SPIDER_CTRL_ORIGINS.
DEFAULT_REMOTE_ORIGINS = ["https://spider-ctrl.vercel.app"]
REMOTE_ORIGINS = [
    o.strip().rstrip("/")
    for o in os.environ.get(
        "SPIDER_CTRL_ORIGINS", ",".join(DEFAULT_REMOTE_ORIGINS)
    ).split(",")
    if o.strip()
]

# Skip launching a browser on boot (headless boxes, service installs).
NO_BROWSER = os.environ.get("SPIDER_CTRL_NO_BROWSER", "").lower() in ("1", "true", "yes")

LOCAL_IP = get_local_ip()
ALLOWED_ORIGINS = pairing.local_origins(SERVER_PORT, LOCAL_IP) + REMOTE_ORIGINS


# ── Controller Instances ─────────────────────────────────────────────────────
mouse = MouseController()
keyboard = KeyboardController()
power = PowerController()
apps = AppController()
search = SearchController()
volume = VolumeController()
media = MediaController()
clipboard = ClipboardController()
system_info = SystemInfoController()
screen = ScreenController()
terminal = TerminalController()
processes = ProcessController()
filesystem = FilesystemController()

# ── Route Dispatch Table ─────────────────────────────────────────────────────
HANDLERS = {
    # Mouse
    "mouse_move": mouse.move,
    "mouse_click": mouse.click,
    "mouse_double_click": mouse.double_click,
    "mouse_right_click": mouse.right_click,
    "mouse_scroll": mouse.scroll,
    "mouse_drag_start": mouse.drag_start,
    "mouse_drag_move": mouse.drag_move,
    "mouse_drag_end": mouse.drag_end,
    # Keyboard
    "key_press": keyboard.press,
    "key_combo": keyboard.combo,
    "key_type": keyboard.type_text,
    # Power
    "power_shutdown": power.shutdown,
    "power_restart": power.restart,
    "power_sleep": power.sleep,
    "power_lock": power.lock,
    "power_logout": power.logout,
    # Apps
    "app_open": apps.open_app,
    "app_list": apps.list_apps,
    "app_close": apps.close_app,
    # Search
    "google_search": search.google_search,
    "url_open": search.open_url,
    # Volume
    "volume_set": volume.set_volume,
    "volume_get": volume.get_volume,
    "volume_mute": volume.toggle_mute,
    "volume_up": volume.volume_up,
    "volume_down": volume.volume_down,
    # Media
    "media_play_pause": media.play_pause,
    "media_next": media.next_track,
    "media_prev": media.prev_track,
    "media_stop": media.stop,
    # Clipboard
    "clipboard_get": clipboard.get_text,
    "clipboard_set": clipboard.set_text,
    # System Info
    "system_info": system_info.get_info,
    # Terminal
    "terminal_execute": terminal.execute,
    "terminal_cwd": terminal.get_cwd,
    "terminal_set_cwd": terminal.set_cwd,
    "terminal_reset": terminal.reset,
    # Process Manager
    "process_list": processes.list_processes,
    "process_kill": processes.kill_process,
    "process_detail": processes.get_process_detail,
    # File Browser
    "fs_list": filesystem.list_directory,
    "fs_drives": filesystem.get_drives,
    "fs_info": filesystem.get_file_info,
}


# ── UDP Discovery Broadcast ─────────────────────────────────────────────────
def udp_broadcast_loop():
    """Broadcasts server presence on the local network every few seconds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    local_ip = get_local_ip()
    hostname = socket.gethostname()

    payload = json.dumps({
        "service": APP_NAME,
        "version": PROTOCOL_VERSION,
        "ip": local_ip,
        "port": SERVER_PORT,
        "hostname": hostname,
        "platform": platform.system(),
    }).encode("utf-8")

    print(f"  📡  UDP broadcast on port {UDP_PORT}  (IP: {local_ip})")

    while True:
        try:
            sock.sendto(payload, ("<broadcast>", UDP_PORT))
        except Exception:
            pass
        time.sleep(BROADCAST_INTERVAL)


# ── FastAPI App ──────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start UDP discovery in a daemon thread
    t = threading.Thread(target=udp_broadcast_loop, daemon=True)
    t.start()
    local_ip = LOCAL_IP
    has_frontend = FRONTEND_DIR.exists()
    http_proto = "https" if ENABLE_TLS else "http"
    ws_proto = "wss" if ENABLE_TLS else "ws"

    token = pairing.get_token()
    code, _ = pairing.pair_code.current()
    pair_url = _pair_url(token)
    setup_url = f"{http_proto}://localhost:{SERVER_PORT}/"

    print("\n" + "═" * 56)
    print(f"  🖥️  {APP_NAME} v{PROTOCOL_VERSION}")
    print(f"  🔌  WebSocket  →  {ws_proto}://{local_ip}:{SERVER_PORT}/ws")
    print(f"  🎥  WebRTC     →  /webrtc/offer")
    print(f"  📡  UDP Disco   →  port {UDP_PORT}")
    print(f"  🔒  TLS         →  {'enabled' if ENABLE_TLS else 'disabled (set SPIDER_CTRL_TLS=1)'}")
    print(f"  💻  Platform    →  {platform.system()} {platform.release()}")
    print("═" * 56)

    if has_frontend:
        qr = pairing.qr_ascii(pair_url)
        if qr:
            print("\n  📱  Scan this with your phone's camera:\n")
            print(qr)
        print(f"  🔗  Or open on phone →  {http_proto}://{local_ip}:{SERVER_PORT}")
        print(f"  🔑  Pairing code     →  {pairing.format_code(code)}")
        print(f"  🖥️  Setup screen     →  {setup_url}")
    else:
        print("\n  ⚠️  Frontend not built — run: cd frontend && npm run build")
    print("═" * 56 + "\n")

    if has_frontend and not NO_BROWSER:
        # Opens the setup screen so the QR is on screen without the user
        # having to find the terminal. Never fatal — headless hosts just skip it.
        def _open_setup():
            time.sleep(1.0)
            try:
                import webbrowser
                webbrowser.open(setup_url)
            except Exception:
                pass

        threading.Thread(target=_open_setup, daemon=True).start()

    yield
    # Shutdown: clean up all WebRTC connections
    await screen.cleanup_all()


app = FastAPI(title=APP_NAME, version=PROTOCOL_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registered after CORSMiddleware, so it wraps it and can annotate the
# preflight response CORS generates.
@app.middleware("http")
async def private_network_access(request: Request, call_next):
    """
    Answer Chrome's Private Network Access preflight.

    A public HTTPS page reaching a private address (the deployed site
    probing http://127.0.0.1:8765/pair) is preflighted with
    Access-Control-Request-Private-Network, and Chrome drops the response
    unless we opt in explicitly. Only granted to origins already on the
    CORS allowlist.
    """
    response = await call_next(request)
    origin = request.headers.get("origin")
    if (
        origin in ALLOWED_ORIGINS
        and request.headers.get("access-control-request-private-network") == "true"
    ):
        response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ip": get_local_ip(),
        "port": SERVER_PORT,
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "webrtc": True,
        "active_streams": screen.active_connections,
    }


# ── Pairing ──────────────────────────────────────────────────────────────────

def _loopback(request: Request) -> bool:
    """True when the request came from this machine."""
    host = request.client.host if request.client else ""
    return host in ("127.0.0.1", "::1", "localhost")


def _pair_url(token: str) -> str:
    scheme = "https" if ENABLE_TLS else "http"
    return f"{scheme}://{LOCAL_IP}:{SERVER_PORT}/?t={token}"


@app.get("/pair")
async def pair(request: Request):
    """
    Hand the pairing token to the setup screen, as a QR code and a URL.

    Loopback only. Two separate locks guard this, because they stop different
    attacks: the loopback check keeps other devices on the Wi-Fi from simply
    asking for the token, and the CORS allowlist keeps a hostile site the user
    happens to have open from reading the response — that request does come
    from loopback, so the first check alone would let it through.
    """
    if not _loopback(request):
        return JSONResponse(
            {"error": "Pairing info is only available on the host machine."},
            status_code=403,
        )

    origin = request.headers.get("origin")
    if origin is not None and origin not in ALLOWED_ORIGINS:
        return JSONResponse({"error": "Origin not allowed."}, status_code=403)

    token = pairing.get_token()
    code, expires_in = pairing.pair_code.current()
    url = _pair_url(token)

    return JSONResponse({
        "hostname": socket.gethostname(),
        "ip": LOCAL_IP,
        "port": SERVER_PORT,
        "platform": platform.system(),
        "version": PROTOCOL_VERSION,
        "url": url,
        "token": token,
        "code": pairing.format_code(code),
        "code_expires_in": expires_in,
        "qr": pairing.qr_data_uri(url),
    })


@app.post("/pair/claim")
async def pair_claim(request: Request):
    """
    Trade a six-character pairing code for the real token.

    Reachable from the LAN — this is the path a phone takes when it can't scan
    the QR. The code is short, so it carries its own defences: single use,
    CODE_TTL expiry, and a hard attempt cap (see utils/pairing.py).
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    if not pairing.pair_code.claim(body.get("code")):
        return JSONResponse(
            {"error": "Invalid or expired pairing code."},
            status_code=403,
        )

    print("  🔑  Pairing code claimed — device paired")
    return JSONResponse({
        "token": pairing.get_token(),
        "hostname": socket.gethostname(),
        "ip": LOCAL_IP,
        "port": SERVER_PORT,
    })


@app.post("/pair/rotate")
async def pair_rotate(request: Request):
    """Issue a new token, dropping every paired device. Loopback only."""
    if not _loopback(request):
        return JSONResponse({"error": "Forbidden"}, status_code=403)
    token = pairing.rotate_token()
    pairing.pair_code.issue()
    print("  🔄  Pairing token rotated — all devices unpaired")
    return JSONResponse({"ok": True, "url": _pair_url(token)})


# ── WebRTC Signaling Endpoints ───────────────────────────────────────────────

@app.post("/webrtc/offer")
async def webrtc_offer(request: Request):
    """Receive SDP offer from client, return SDP answer."""
    try:
        body = await request.json()
        sdp = body.get("sdp")
        sdp_type = body.get("type", "offer")
        quality = body.get("quality", "medium")

        if not sdp:
            return JSONResponse(
                {"error": "Missing 'sdp' in request body"},
                status_code=400,
            )

        result = await screen.create_offer(
            sdp=sdp, sdp_type=sdp_type, quality=quality
        )
        return JSONResponse(result)

    except Exception as exc:
        logger.error(f"WebRTC offer error: {exc}")
        return JSONResponse(
            {"error": str(exc)},
            status_code=500,
        )


@app.post("/webrtc/ice")
async def webrtc_ice(request: Request):
    """Receive trickle ICE candidate."""
    try:
        body = await request.json()
        connection_id = body.get("connection_id")
        candidate = body.get("candidate")

        if not connection_id or not candidate:
            return JSONResponse(
                {"error": "Missing 'connection_id' or 'candidate'"},
                status_code=400,
            )

        result = await screen.add_ice_candidate(connection_id, candidate)
        return JSONResponse(result)

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/webrtc/quality")
async def webrtc_quality(request: Request):
    """Change stream quality for a connection."""
    try:
        body = await request.json()
        connection_id = body.get("connection_id")
        quality = body.get("quality", "medium")

        if not connection_id:
            return JSONResponse(
                {"error": "Missing 'connection_id'"},
                status_code=400,
            )

        result = await screen.change_quality(connection_id, quality)
        return JSONResponse(result)

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/webrtc/stop")
async def webrtc_stop(request: Request):
    """Stop a specific stream."""
    try:
        body = await request.json()
        connection_id = body.get("connection_id")

        if not connection_id:
            return JSONResponse(
                {"error": "Missing 'connection_id'"},
                status_code=400,
            )

        result = await screen.stop_stream(connection_id)
        return JSONResponse(result)

    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/webrtc/stats/{connection_id}")
async def webrtc_stats(connection_id: str):
    """Get stream statistics."""
    result = await screen.get_stats(connection_id)
    return JSONResponse(result)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    # Browsers do not apply CORS to WebSocket handshakes, so without this any
    # page the user has open could connect to ws://127.0.0.1:8765/ws and drive
    # the machine through HANDLERS.
    #
    # The handshake is accepted before the check and then closed on failure,
    # rather than refused outright: refusing pre-accept makes Starlette answer
    # the upgrade with a plain HTTP 403, which reaches the browser as close
    # code 1006 — indistinguishable from the server being down, so the client
    # would retry a token that can never work. Accepting first delivers a real
    # 1008, which tells it to stop and re-pair. Nothing is read from the socket
    # before it closes, so no command can run.
    client = ws.client
    origin = ws.headers.get("origin")
    await ws.accept()

    if not pairing.is_origin_allowed(origin, SERVER_PORT, set(REMOTE_ORIGINS)):
        print(f"  🚫  Rejected handshake from disallowed origin: {origin}")
        await ws.close(code=1008, reason="origin not allowed")
        return

    if not pairing.verify_token(ws.query_params.get("t")):
        host = client.host if client else "?"
        print(f"  🚫  Rejected unpaired client: {host}")
        await ws.close(code=1008, reason="not paired")
        return

    print(f"  ✅  Client connected: {client.host}:{client.port}")

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"error": "Invalid JSON"})
                continue

            action = msg.get("action")
            payload = msg.get("payload", {})
            request_id = msg.get("id")

            handler = HANDLERS.get(action)
            if handler is None:
                resp = {"error": f"Unknown action: {action}"}
            else:
                try:
                    # Run sync handlers in a thread to avoid blocking
                    # the event loop (critical for long-running commands
                    # like terminal_execute or process_list).
                    if payload:
                        result = await asyncio.to_thread(handler, **payload)
                    else:
                        result = await asyncio.to_thread(handler)
                    resp = {"ok": True, "data": result}
                except Exception as exc:
                    resp = {"ok": False, "error": str(exc)}

            if request_id is not None:
                resp["id"] = request_id

            await ws.send_json(resp)

    except WebSocketDisconnect:
        print(f"  ❌  Client disconnected: {client.host}:{client.port}")
    except Exception as exc:
        print(f"  ⚠️  Error: {exc}")


# ── Serve Frontend ───────────────────────────────────────────────────────────
if FRONTEND_DIR.exists():
    # Serve Next.js static export from /frontend/out
    def _safe_path(rel: str) -> Path | None:
        """
        Resolve `rel` inside FRONTEND_DIR, or return None if it escapes.

        Uvicorn hands us the raw request target, so "../../secret" would
        otherwise walk out of the export directory.
        """
        try:
            candidate = (FRONTEND_DIR / rel).resolve()
        except (OSError, ValueError):
            return None
        if candidate != FRONTEND_DIR and FRONTEND_DIR not in candidate.parents:
            return None
        return candidate if candidate.is_file() else None

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve the static frontend. Falls back to index.html for SPA routing."""
        file_path = _safe_path(path)
        if file_path:
            return FileResponse(file_path)
        # Try .html extension (Next.js exports pages as page.html)
        html_path = _safe_path(f"{path}.html")
        if html_path:
            return FileResponse(html_path)
        # Fallback to index.html
        index_path = FRONTEND_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        return {"error": "Frontend not built. Run: cd frontend && npm run build"}

    print(f"  📂  Frontend found at {FRONTEND_DIR}")
else:
    @app.get("/")
    async def no_frontend():
        return {
            "message": "SPIDER_CTRL Server is running. Frontend not found.",
            "hint": "Run: cd frontend && npm run build",
            "websocket": f"ws://{get_local_ip()}:{SERVER_PORT}/ws",
        }


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_kwargs = dict(
        host="0.0.0.0",
        port=SERVER_PORT,
        log_level="warning",
        reload=False,
    )

    if ENABLE_TLS:
        cert_path, key_path = ensure_ssl_certs(get_local_ip())
        run_kwargs["ssl_certfile"] = cert_path
        run_kwargs["ssl_keyfile"] = key_path

    uvicorn.run("server:app", **run_kwargs)

