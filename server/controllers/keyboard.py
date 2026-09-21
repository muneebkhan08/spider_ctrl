"""Keyboard controller — press keys, combos, type text."""

import platform

import pyautogui

from .clipboard import ClipboardController

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0


class KeyboardController:
    # Map friendly names to pyautogui key names
    KEY_MAP = {
        "enter": "enter",
        "return": "enter",
        "tab": "tab",
        "space": "space",
        "backspace": "backspace",
        "delete": "delete",
        "escape": "esc",
        "esc": "esc",
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "home": "home",
        "end": "end",
        "pageup": "pageup",
        "pagedown": "pagedown",
        "capslock": "capslock",
        "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
        "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
        "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
        "ctrl": "ctrl",
        "alt": "alt",
        "shift": "shift",
        "win": "win",
        "super": "win",
        "meta": "win",
        "printscreen": "printscreen",
        "insert": "insert",
        "numlock": "numlock",
        "scrolllock": "scrolllock",
        "pause": "pause",
    }

    # On macOS the "Windows/Super" key is Command, and Ctrl-shortcuts are
    # Command-shortcuts; pyautogui names that key "command".
    MAC_OVERRIDES = {"win": "command", "ctrl": "command"}

    def __init__(self):
        self._is_mac = platform.system() == "Darwin"

    def _resolve_key(self, key: str) -> str:
        resolved = self.KEY_MAP.get(key.lower(), key)
        if self._is_mac:
            resolved = self.MAC_OVERRIDES.get(resolved, resolved)
        return resolved

    def press(self, key: str = "", **_):
        """Press a single key."""
        resolved = self._resolve_key(key)
        pyautogui.press(resolved)
        return {"pressed": resolved}

    def combo(self, keys: list = None, **_):
        """Press a key combination like Ctrl+C."""
        if not keys:
            return {"error": "No keys provided"}
        resolved = [self._resolve_key(k) for k in keys]
        pyautogui.hotkey(*resolved)
        return {"combo": resolved}

    def type_text(self, text: str = "", **_):
        """Type a string of text."""
        if not text:
            return {"typed": 0}
        if text.isascii():
            pyautogui.typewrite(text, interval=0.02)
        else:
            self._type_unicode(text)
        return {"typed": len(text)}

    def _type_unicode(self, text: str):
        """
        pyautogui cannot synthesise non-ASCII characters, so route them
        through the clipboard and paste instead.
        """
        result = ClipboardController().set_text(text)
        if result.get("error"):
            raise RuntimeError(f"Cannot type unicode text: {result['error']}")
        modifier = "command" if self._is_mac else "ctrl"
        pyautogui.hotkey(modifier, "v")
