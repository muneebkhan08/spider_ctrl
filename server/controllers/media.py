"""
Media controller — play/pause, next, prev, stop.

Windows and Linux take the ordinary virtual key presses pyautogui provides.
macOS does not: pyautogui maps every media key to None there, so
`pyautogui.press("playpause")` is a silent no-op. Media keys on macOS are
NSSystemDefined events, not keyboard events, so they are posted directly.
"""

import platform

import pyautogui

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

SYSTEM = platform.system()

# NX_KEYTYPE_* constants from IOKit's hidsystem/ev_keymap.h.
NX_KEYTYPE_PLAY = 16
NX_KEYTYPE_NEXT = 17
NX_KEYTYPE_PREVIOUS = 18

# NSEvent.type for a system-defined event, and the subtype media keys use.
NS_SYSTEM_DEFINED = 14
NS_SUBTYPE_AUX_CONTROL = 8


def _macos_media_key(key: int) -> bool:
    """
    Post a media key as a system-defined event. Returns True if it went out.

    The down and up events are distinguished by the 0xa / 0xb nibble packed
    into data1 and mirrored in the modifier flags, which is what the window
    server inspects.
    """
    try:
        import Quartz
        from AppKit import NSEvent
    except Exception:
        return False

    try:
        for down in (True, False):
            data1 = (key << 16) | ((0xA if down else 0xB) << 8)
            event = NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
                NS_SYSTEM_DEFINED,
                (0, 0),
                0xA00 if down else 0xB00,
                0,
                0,
                None,
                NS_SUBTYPE_AUX_CONTROL,
                data1,
                -1,
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, event.CGEvent())
        return True
    except Exception:
        return False


class MediaController:
    def _send(self, mac_key: int | None, pyautogui_key: str, label: str) -> dict:
        if SYSTEM == "Darwin":
            if mac_key is None:
                # macOS has no system-wide stop key. Say so rather than
                # returning a success the user cannot observe.
                return {"media": label, "sent": False,
                        "note": "macOS has no system-wide stop key — use pause instead."}
            return {"media": label, "sent": _macos_media_key(mac_key)}

        pyautogui.press(pyautogui_key)
        return {"media": label, "sent": True}

    def play_pause(self, **_):
        return self._send(NX_KEYTYPE_PLAY, "playpause", "play_pause")

    def next_track(self, **_):
        return self._send(NX_KEYTYPE_NEXT, "nexttrack", "next")

    def prev_track(self, **_):
        return self._send(NX_KEYTYPE_PREVIOUS, "prevtrack", "prev")

    def stop(self, **_):
        return self._send(None, "stop", "stop")
