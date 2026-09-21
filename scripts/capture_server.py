"""
FastAPI server for capturing live screenshots of the working SPIDER_CTRL app.
Serves frontend/out and handles WebSocket requests with live system controllers.
"""

import asyncio
import json
import logging
from pathlib import Path
import platform
import sys

# Add server directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "server"))

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from controllers.system_info import SystemInfoController
from controllers.processes import ProcessController
from controllers.filesystem import FilesystemController
from controllers.terminal import TerminalController
from controllers.apps import AppController
from controllers.volume import VolumeController
from controllers.power import PowerController
from controllers.search import SearchController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("capture_server")

SERVER_PORT = 8765
FRONTEND_DIR = (Path(__file__).resolve().parent.parent / "frontend" / "out").resolve()

# Real controllers
system_info = SystemInfoController()
processes = ProcessController()
filesystem = FilesystemController()
terminal = TerminalController()
apps = AppController()
volume = VolumeController()
power = PowerController()
search = SearchController()

# Dummy handlers for input
def dummy_ok(**_):
    return {"status": "ok"}

HANDLERS = {
    # Mouse & Keyboard dummy
    "mouse_move": dummy_ok,
    "mouse_click": dummy_ok,
    "mouse_double_click": dummy_ok,
    "mouse_right_click": dummy_ok,
    "mouse_scroll": dummy_ok,
    "mouse_drag_start": dummy_ok,
    "mouse_drag_move": dummy_ok,
    "mouse_drag_end": dummy_ok,
    "key_press": dummy_ok,
    "key_combo": dummy_ok,
    "key_type": dummy_ok,
    # Live controllers
    "system_info": system_info.get_info,
    "process_list": processes.list_processes,
    "process_kill": processes.kill_process,
    "process_detail": processes.get_process_detail,
    "fs_list": filesystem.list_directory,
    "fs_drives": filesystem.get_drives,
    "fs_info": filesystem.get_file_info,
    "terminal_execute": terminal.execute,
    "terminal_cwd": terminal.get_cwd,
    "terminal_set_cwd": terminal.set_cwd,
    "terminal_reset": terminal.reset,
    "app_open": apps.open_app,
    "app_list": apps.list_apps,
    "app_close": apps.close_app,
    "volume_set": volume.set_volume,
    "volume_get": volume.get_volume,
    "volume_mute": volume.toggle_mute,
    "volume_up": volume.volume_up,
    "volume_down": volume.volume_down,
    "power_shutdown": power.shutdown,
    "power_restart": power.restart,
    "power_sleep": power.sleep,
    "power_lock": power.lock,
    "power_logout": power.logout,
    "google_search": search.google_search,
    "url_open": search.open_url,
    "media_play_pause": dummy_ok,
    "media_next": dummy_ok,
    "media_prev": dummy_ok,
    "media_stop": dummy_ok,
    "clipboard_get": lambda **_: {"text": "SPIDER_CTRL Remote Clipboard"},
    "clipboard_set": dummy_ok,
}

app = FastAPI(title="SPIDER_CTRL Capture Server")

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
        "ip": "127.0.0.1",
        "port": SERVER_PORT,
        "hostname": "SPIDER-MAC",
        "platform": platform.system(),
        "webrtc": True,
        "active_connections": 1,
    }

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    logger.info("WebSocket client connected")
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
        logger.info("WebSocket client disconnected")
    except Exception as exc:
        logger.error(f"WebSocket error: {exc}")

if FRONTEND_DIR.exists():
    def _safe_path(rel: str) -> Path | None:
        try:
            candidate = (FRONTEND_DIR / rel).resolve()
        except (OSError, ValueError):
            return None
        if candidate != FRONTEND_DIR and FRONTEND_DIR not in candidate.parents:
            return None
        return candidate if candidate.is_file() else None

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = _safe_path(path)
        if file_path:
            return FileResponse(file_path)
        html_path = _safe_path(f"{path}.html")
        if html_path:
            return FileResponse(html_path)
        index_path = FRONTEND_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        return {"error": "Frontend not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT, log_level="warning")
