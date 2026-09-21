"""Clipboard controller — get/set clipboard text (Windows, macOS, Linux)."""

import platform
import shutil
import subprocess


class ClipboardController:
    """
    Reads and writes the system clipboard using whatever native helper
    the host provides:

      Windows  →  PowerShell Get-Clipboard / Set-Clipboard
      macOS    →  pbpaste / pbcopy
      Linux    →  wl-paste / wl-copy (Wayland), else xclip, else xsel
    """

    def __init__(self):
        self._system = platform.system()

    # ── Public API ───────────────────────────────────────────────────────

    def get_text(self, **_):
        try:
            cmd = self._read_command()
            if cmd is None:
                return {"error": self._unsupported_message()}
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return {"error": (result.stderr or "Clipboard read failed").strip()}
            return {"text": result.stdout.strip()}
        except Exception as exc:
            return {"error": str(exc)}

    def set_text(self, text: str = "", **_):
        try:
            cmd = self._write_command(text)
            if cmd is None:
                return {"error": self._unsupported_message()}
            # PowerShell takes the value as an argument; the Unix helpers
            # read it from stdin.
            if self._system == "Windows":
                result = subprocess.run(cmd, capture_output=True, text=True)
            else:
                result = subprocess.run(
                    cmd, input=text, capture_output=True, text=True
                )
            if result.returncode != 0:
                return {"error": (result.stderr or "Clipboard write failed").strip()}
            return {"copied": True}
        except Exception as exc:
            return {"error": str(exc)}

    # ── Internal helpers ─────────────────────────────────────────────────

    def _read_command(self) -> list[str] | None:
        if self._system == "Windows":
            return ["powershell", "-NoProfile", "-Command", "Get-Clipboard"]
        if self._system == "Darwin":
            return ["pbpaste"]
        for tool, args in (
            ("wl-paste", ["wl-paste", "--no-newline"]),
            ("xclip", ["xclip", "-selection", "clipboard", "-o"]),
            ("xsel", ["xsel", "--clipboard", "--output"]),
        ):
            if shutil.which(tool):
                return args
        return None

    def _write_command(self, text: str) -> list[str] | None:
        if self._system == "Windows":
            # -EncodedCommand would be safer still, but escaping the quote
            # is enough here: the value never leaves the argument position.
            safe = text.replace("'", "''")
            return [
                "powershell", "-NoProfile", "-Command",
                f"Set-Clipboard -Value '{safe}'",
            ]
        if self._system == "Darwin":
            return ["pbcopy"]
        for tool, args in (
            ("wl-copy", ["wl-copy"]),
            ("xclip", ["xclip", "-selection", "clipboard"]),
            ("xsel", ["xsel", "--clipboard", "--input"]),
        ):
            if shutil.which(tool):
                return args
        return None

    def _unsupported_message(self) -> str:
        if self._system == "Linux":
            return "No clipboard tool found. Install wl-clipboard, xclip, or xsel."
        return f"Clipboard not supported on {self._system}"
