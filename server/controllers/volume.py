"""
Volume controller.

  Windows  →  pycaw (Core Audio endpoint volume)
  macOS    →  osascript (`set volume output volume …`)
  Linux    →  pactl (PulseAudio / PipeWire)
"""

import platform
import re
import shutil
import subprocess


class VolumeController:
    def __init__(self):
        self._system = platform.system()
        self._windows_volume = None
        if self._system == "Windows":
            try:
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                self._windows_volume = cast(
                    interface, POINTER(IAudioEndpointVolume)
                )
            except Exception:
                pass

    # ── Public API ───────────────────────────────────────────────────────

    def get_volume(self, **_):
        if self._windows_volume:
            level = self._windows_volume.GetMasterVolumeLevelScalar()
            muted = self._windows_volume.GetMute()
            return {"volume": round(level * 100), "muted": bool(muted)}

        if self._system == "Darwin":
            return self._mac_get()

        if self._system == "Linux":
            return self._linux_get()

        return {"volume": -1, "muted": False}

    def set_volume(self, level: int = 50, **_):
        level = max(0, min(100, int(level)))

        if self._windows_volume:
            self._windows_volume.SetMasterVolumeLevelScalar(level / 100, None)
            return {"volume": level}

        if self._system == "Darwin":
            self._osascript(f"set volume output volume {level}")
            return {"volume": level}

        if self._system == "Linux" and shutil.which("pactl"):
            self._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"])
            return {"volume": level}

        return {"error": self._unsupported_message()}

    def volume_up(self, step: int = 5, **_):
        info = self.get_volume()
        current = info.get("volume", 50)
        if current < 0:
            current = 50
        return self.set_volume(level=min(100, current + step))

    def volume_down(self, step: int = 5, **_):
        info = self.get_volume()
        current = info.get("volume", 50)
        if current < 0:
            current = 50
        return self.set_volume(level=max(0, current - step))

    def toggle_mute(self, **_):
        if self._windows_volume:
            current = bool(self._windows_volume.GetMute())
            self._windows_volume.SetMute(not current, None)
            return {"muted": not current}

        if self._system == "Darwin":
            muted = self.get_volume().get("muted", False)
            self._osascript(
                f"set volume output muted {'false' if muted else 'true'}"
            )
            return {"muted": not muted}

        if self._system == "Linux" and shutil.which("pactl"):
            self._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
            return {"muted": self._linux_get().get("muted", False)}

        return {"error": self._unsupported_message()}

    # ── Platform helpers ─────────────────────────────────────────────────

    def _mac_get(self) -> dict:
        # Two calls rather than one: AppleScript's `&` coerces the pair into
        # a list and prints "31, ,, true", which is awkward to parse back.
        level = self._osascript("output volume of (get volume settings)")
        muted = self._osascript("output muted of (get volume settings)")
        try:
            return {
                "volume": int(level),
                "muted": muted.strip().lower() == "true",
            }
        except (ValueError, TypeError):
            return {"volume": -1, "muted": False}

    def _linux_get(self) -> dict:
        if not shutil.which("pactl"):
            return {"volume": -1, "muted": False}

        volume = -1
        out = self._run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"])
        match = re.search(r"(\d+)%", out or "")
        if match:
            volume = int(match.group(1))

        muted = False
        mute_out = self._run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"])
        if mute_out:
            muted = "yes" in mute_out.lower()

        return {"volume": volume, "muted": muted}

    @staticmethod
    def _run(cmd: list[str]) -> str:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        except Exception:
            return ""

    @staticmethod
    def _osascript(script: str) -> str:
        try:
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _unsupported_message(self) -> str:
        if self._system == "Windows":
            return "pycaw not available — install pycaw and comtypes."
        if self._system == "Linux":
            return "pactl not found — install pulseaudio-utils."
        return f"Volume control not supported on {self._system}"
