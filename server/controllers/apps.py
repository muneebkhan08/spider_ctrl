"""App controller — open, close, list running applications."""

import subprocess
import platform
import os

_SYSTEM = platform.system()

# ── Platform-specific app catalogues ─────────────────────────────────────────
# Each maps a user-friendly name → the launch token for that platform.

_APPS_WIN = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "task manager": "taskmgr.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "settings": "ms-settings:",
    "control panel": "control.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "spotify": "spotify.exe",
    "discord": "discord.exe",
    "slack": "slack.exe",
    "vs code": "code.exe",
    "visual studio code": "code.exe",
    "obs": "obs64.exe",
    "vlc": "vlc.exe",
    "steam": "steam.exe",
    "terminal": "wt.exe",
    "snipping tool": "snippingtool.exe",
}

_APPS_MAC = {
    "finder": "Finder",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "firefox": "Firefox",
    "edge": "Microsoft Edge",
    "terminal": "Terminal",
    "iterm": "iTerm",
    "activity monitor": "Activity Monitor",
    "system preferences": "System Preferences",
    "system settings": "System Settings",
    "calculator": "Calculator",
    "notes": "Notes",
    "textedit": "TextEdit",
    "preview": "Preview",
    "music": "Music",
    "spotify": "Spotify",
    "discord": "Discord",
    "slack": "Slack",
    "zoom": "zoom.us",
    "teams": "Microsoft Teams",
    "vs code": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "outlook": "Microsoft Outlook",
    "vlc": "VLC",
    "obs": "OBS",
    "steam": "Steam",
}

_APPS_LINUX = {
    "file manager": "nautilus",
    "files": "nautilus",
    "terminal": "gnome-terminal",
    "calculator": "gnome-calculator",
    "text editor": "gedit",
    "settings": "gnome-control-center",
    "chrome": "google-chrome",
    "chromium": "chromium-browser",
    "firefox": "firefox",
    "edge": "microsoft-edge",
    "spotify": "spotify",
    "discord": "discord",
    "slack": "slack",
    "zoom": "zoom",
    "teams": "teams",
    "vs code": "code",
    "visual studio code": "code",
    "vlc": "vlc",
    "obs": "obs",
    "steam": "steam",
    "libreoffice writer": "libreoffice --writer",
    "libreoffice calc": "libreoffice --calc",
    "libreoffice impress": "libreoffice --impress",
}

# Select the right catalogue at import time
if _SYSTEM == "Windows":
    COMMON_APPS = _APPS_WIN
elif _SYSTEM == "Darwin":
    COMMON_APPS = _APPS_MAC
else:
    COMMON_APPS = _APPS_LINUX


class AppController:
    def open_app(self, name: str = "", path: str = "", **_):
        """Open an application by friendly name or direct path."""
        if path:
            subprocess.Popen(path, shell=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return {"opened": path}

        name_lower = name.lower().strip()
        app_token = COMMON_APPS.get(name_lower)

        # Use the catalogue token, or fall back to whatever the user typed
        target = app_token or name

        try:
            if _SYSTEM == "Windows":
                if target.startswith("ms-"):
                    os.startfile(target)
                else:
                    subprocess.Popen(target, shell=True)
            elif _SYSTEM == "Darwin":
                # macOS: `open -a <AppName>` handles .app bundles
                subprocess.Popen(
                    ["open", "-a", target],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Linux: launch the binary directly
                subprocess.Popen(
                    target, shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return {"opened": name}
        except Exception as e:
            return {"error": f"Could not open {name}: {str(e)}"}

    def list_apps(self, **_):
        """Return list of available quick-launch apps + running processes."""
        running = []
        try:
            import psutil
            seen: set[str] = set()
            for proc in psutil.process_iter(["name", "pid"]):
                info = proc.info
                if info["name"] and info["name"] not in seen:
                    seen.add(info["name"])
                    running.append({"name": info["name"], "pid": info["pid"]})
        except Exception:
            pass

        return {
            "quick_launch": sorted(COMMON_APPS.keys()),
            "running": running[:50],
        }

    def close_app(self, name: str = "", pid: int = None, **_):
        """Close an application by name or PID."""
        if pid:
            try:
                import psutil
                proc = psutil.Process(pid)
                proc.terminate()
                return {"closed": pid}
            except Exception as e:
                return {"error": str(e)}

        name_lower = name.lower().strip()
        app_token = COMMON_APPS.get(name_lower, name)

        if _SYSTEM == "Windows":
            subprocess.Popen(f'taskkill /IM "{app_token}" /F', shell=True)
        elif _SYSTEM == "Darwin":
            # macOS: quit gracefully via osascript, then force-kill if needed
            subprocess.Popen(
                ["osascript", "-e",
                 f'tell application "{app_token}" to quit'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(f"pkill -f {app_token}", shell=True)
        return {"closed": name}
