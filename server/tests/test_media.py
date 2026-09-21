"""
Tests for the media controller.

pyautogui maps every media key to None on macOS, so the previous
implementation posted nothing and reported success — the MEDIA buttons did
nothing at all. These tests pin the platform split so that cannot return.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from controllers import media  # noqa: E402


@pytest.fixture
def controller():
    return media.MediaController()


def test_pyautogui_media_keys_are_unusable_on_macos():
    """
    Documents *why* the macOS branch exists.

    If pyautogui ever gains real macOS media-key support this fails, and the
    special case can be reconsidered.
    """
    if sys.platform != "darwin":
        pytest.skip("macOS only")
    import pyautogui._pyautogui_osx as osx
    mapping = getattr(osx, "keyboardMapping", {})
    assert all(mapping.get(k) is None for k in ("playpause", "nexttrack", "prevtrack"))


@pytest.mark.parametrize("action", ["play_pause", "next_track", "prev_track"])
def test_transport_keys_report_being_sent(controller, action, monkeypatch):
    monkeypatch.setattr(media, "_macos_media_key", lambda key: True)
    monkeypatch.setattr(media.pyautogui, "press", lambda key: None)
    result = getattr(controller, action)()
    assert result["sent"] is True


def test_macos_uses_nsevent_not_pyautogui(controller, monkeypatch):
    monkeypatch.setattr(media, "SYSTEM", "Darwin")
    pressed = []
    monkeypatch.setattr(media.pyautogui, "press", lambda key: pressed.append(key))
    posted = []
    monkeypatch.setattr(media, "_macos_media_key", lambda key: posted.append(key) or True)

    controller.play_pause()
    assert posted == [media.NX_KEYTYPE_PLAY]
    assert pressed == [], "macOS must not fall through to pyautogui"


def test_other_platforms_use_pyautogui(controller, monkeypatch):
    monkeypatch.setattr(media, "SYSTEM", "Windows")
    pressed = []
    monkeypatch.setattr(media.pyautogui, "press", lambda key: pressed.append(key))
    controller.next_track()
    assert pressed == ["nexttrack"]


def test_stop_is_honest_about_macos(controller, monkeypatch):
    """macOS has no system-wide stop key; reporting success would be a lie."""
    monkeypatch.setattr(media, "SYSTEM", "Darwin")
    result = controller.stop()
    assert result["sent"] is False
    assert "note" in result


def test_a_failed_post_is_reported(controller, monkeypatch):
    monkeypatch.setattr(media, "SYSTEM", "Darwin")
    monkeypatch.setattr(media, "_macos_media_key", lambda key: False)
    assert controller.play_pause()["sent"] is False


def test_real_macos_post_succeeds(controller):
    """The genuine path, on a real Mac. Harmless with no media app running."""
    if sys.platform != "darwin":
        pytest.skip("macOS only")
    assert media._macos_media_key(media.NX_KEYTYPE_PLAY) is True
