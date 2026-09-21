"""Power controller — shutdown, restart, sleep, lock, logout."""

import subprocess
import platform

_SYSTEM = platform.system()


class PowerController:
    def _run(self, cmd: str):
        """Run a shell command in the background without blocking."""
        subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def shutdown(self, delay: int = 0, **_):
        if _SYSTEM == "Windows":
            self._run(f"shutdown /s /t {delay}")
        elif _SYSTEM == "Darwin":
            # macOS: osascript tells System Events to shut down
            if delay > 0:
                self._run(
                    f"sleep {delay} && osascript -e "
                    "'tell app \"System Events\" to shut down'"
                )
            else:
                self._run(
                    'osascript -e \'tell app "System Events" to shut down\''
                )
        else:
            # Linux
            self._run(f"shutdown -h +{delay // 60}")
        return {"action": "shutdown", "delay": delay}

    def restart(self, delay: int = 0, **_):
        if _SYSTEM == "Windows":
            self._run(f"shutdown /r /t {delay}")
        elif _SYSTEM == "Darwin":
            if delay > 0:
                self._run(
                    f"sleep {delay} && osascript -e "
                    "'tell app \"System Events\" to restart'"
                )
            else:
                self._run(
                    'osascript -e \'tell app "System Events" to restart\''
                )
        else:
            self._run(f"shutdown -r +{delay // 60}")
        return {"action": "restart", "delay": delay}

    def sleep(self, **_):
        if _SYSTEM == "Windows":
            self._run(
                "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
            )
        elif _SYSTEM == "Darwin":
            # macOS: pmset is the most reliable sleep trigger
            self._run("pmset sleepnow")
        else:
            self._run("systemctl suspend")
        return {"action": "sleep"}

    def lock(self, **_):
        if _SYSTEM == "Windows":
            self._run("rundll32.exe user32.dll,LockWorkStation")
        elif _SYSTEM == "Darwin":
            # macOS: turn off the display — login required to resume.
            # This is the most universal lock approach on macOS.
            self._run("pmset displaysleepnow")
        else:
            self._run("loginctl lock-session")
        return {"action": "lock"}

    def logout(self, **_):
        if _SYSTEM == "Windows":
            self._run("shutdown /l")
        elif _SYSTEM == "Darwin":
            self._run(
                'osascript -e \'tell app "System Events" to log out\''
            )
        else:
            self._run("loginctl terminate-user $USER")
        return {"action": "logout"}
