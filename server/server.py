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
    local_ip = get_local_ip()
    has_frontend = FRONTEND_DIR.exists()
    http_proto = "https" if ENABLE_TLS else "http"
    ws_proto = "wss" if ENABLE_TLS else "ws"
    print("\n" + "═" * 56)
    print(f"  🖥️  {APP_NAME} v{PROTOCOL_VERSION}")
    if has_frontend:
        print(f"  🌐  Open on phone → {http_proto}://{local_ip}:{SERVER_PORT}")
    else:
        print(f"  ⚠️  Frontend not built — run: cd frontend && npm run build")
    print(f"  🔌  WebSocket  →  {ws_proto}://{local_ip}:{SERVER_PORT}/ws")
    print(f"  🎥  WebRTC     →  /webrtc/offer")
    print(f"  📡  UDP Disco   →  port {UDP_PORT}")
    print(f"  🔒  TLS         →  {'enabled' if ENABLE_TLS else 'disabled (set SPIDER_CTRL_TLS=1)'}")
    print(f"  💻  Platform    →  {platform.system()} {platform.release()}")
    print("═" * 56 + "\n")
    yield
    # Shutdown: clean up all WebRTC connections
    await screen.cleanup_all()


app = FastAPI(title=APP_NAME, version=PROTOCOL_VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    await ws.accept()
    client = ws.client
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

