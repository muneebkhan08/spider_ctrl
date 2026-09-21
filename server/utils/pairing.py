"""
Pairing and token authentication.

Every connection to /ws must present the machine's pairing token. The token is
a 256-bit secret generated on first run and kept in config/pairing.json — it
never changes unless the user rotates it, so a paired phone stays paired.

Getting the token onto the phone happens one of two ways:

  1. QR code (default). The token is baked into the URL, so scanning it pairs
     and connects in one step with nothing to type.
  2. A six-character pairing code, for when the camera isn't an option. The
     code is short enough to read off the screen, so it is deliberately weak
     on its own — it expires after CODE_TTL seconds and dies after
     CODE_MAX_ATTEMPTS wrong guesses. Claiming it returns the real token.

The distinction matters: the token is the credential, the code is only a
short-lived courier for it.
"""

import base64
import hmac
import io
import json
import platform
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

CONFIG_DIR = Path(__file__).parent.parent / "config"
TOKEN_FILE = CONFIG_DIR / "pairing.json"

# Ambiguous glyphs (I/L/O/U, 0/1) are left out so a code read off a screen
# can't be mistyped into a different valid-looking code.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTVWXYZ23456789"
CODE_LENGTH = 6
CODE_TTL = 600  # seconds
CODE_MAX_ATTEMPTS = 5


# ── Token ───────────────────────────────────────────────────────────────────
_token: str | None = None
_lock = threading.Lock()


def _load_token() -> str | None:
    try:
        data = json.loads(TOKEN_FILE.read_text())
    except (OSError, ValueError):
        return None
    token = data.get("token")
    return token if isinstance(token, str) and token else None


def _save_token(token: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps({"token": token}, indent=2))
    # Best-effort: on POSIX keep the secret out of other accounts' reach.
    try:
        TOKEN_FILE.chmod(0o600)
    except OSError:
        pass


def get_token() -> str:
    """Return this machine's pairing token, creating one on first run."""
    global _token
    with _lock:
        if _token is None:
            _token = _load_token() or secrets.token_urlsafe(32)
            _save_token(_token)
        return _token


def rotate_token() -> str:
    """Throw away the current token and issue a new one, unpairing every device."""
    global _token
    with _lock:
        _token = secrets.token_urlsafe(32)
        _save_token(_token)
        return _token


def verify_token(candidate: str | None) -> bool:
    """Constant-time comparison against the stored token."""
    if not candidate:
        return False
    return hmac.compare_digest(candidate, get_token())


# ── Short-lived pairing code ────────────────────────────────────────────────
class _PairCode:
    def __init__(self) -> None:
        self.value = ""
        self.expires_at = 0.0
        self.attempts = 0
        self.lock = threading.Lock()

    def issue(self) -> str:
        with self.lock:
            self.value = "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))
            self.expires_at = time.time() + CODE_TTL
            self.attempts = 0
            return self.value

    def current(self) -> tuple[str, int]:
        """Return (code, seconds_remaining), reissuing if it has lapsed."""
        with self.lock:
            remaining = int(self.expires_at - time.time())
            if not self.value or remaining <= 0:
                remaining = -1
        if remaining <= 0:
            return self.issue(), CODE_TTL
        return self.value, remaining

    def claim(self, candidate: str | None) -> bool:
        """
        Check a user-supplied code. Burns the code on success (one device per
        code) and on too many failures (so it can't be ground down by guessing).
        """
        if not candidate:
            return False
        normalized = candidate.strip().upper().replace("-", "").replace(" ", "")
        with self.lock:
            if not self.value or time.time() > self.expires_at:
                self.value = ""
                return False
            if self.attempts >= CODE_MAX_ATTEMPTS:
                self.value = ""
                return False
            self.attempts += 1
            if hmac.compare_digest(normalized, self.value):
                self.value = ""  # single use
                return True
            if self.attempts >= CODE_MAX_ATTEMPTS:
                self.value = ""
            return False


pair_code = _PairCode()


def format_code(code: str) -> str:
    """Group a code as XXX-XXX so it is easier to read aloud and retype."""
    half = len(code) // 2
    return f"{code[:half]}-{code[half:]}" if half else code


# ── Origins ─────────────────────────────────────────────────────────────────
def local_origins(port: int, local_ip: str) -> list[str]:
    """Every origin the server itself serves the UI from."""
    hosts = ["localhost", "127.0.0.1", local_ip]
    try:
        hosts.append(f"{platform.node().split('.')[0].lower()}.local")
    except Exception:
        pass
    origins: list[str] = []
    for host in dict.fromkeys(h for h in hosts if h):
        origins.append(f"http://{host}:{port}")
        origins.append(f"https://{host}:{port}")
    return origins


def is_origin_allowed(origin: str | None, port: int, extra: set[str]) -> bool:
    """
    Decide whether a browser origin may open a WebSocket.

    The token is the real credential; this is the second lock. A hostile page
    is served from :80 or :443 on its own domain, so requiring the origin's
    port to be our own port rejects it — including a DNS-rebinding attempt,
    which keeps the attacker's port. Non-browser clients send no Origin at all
    and are let through to the token check.
    """
    if not origin:
        return True
    if origin in extra:
        return True
    try:
        parts = urlsplit(origin)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https"):
        return False
    try:
        explicit_port = parts.port
    except ValueError:
        return False
    if explicit_port is None:
        explicit_port = 443 if parts.scheme == "https" else 80
    return explicit_port == port


# ── QR rendering ────────────────────────────────────────────────────────────
def qr_ascii(url: str) -> str | None:
    """Render `url` as a QR code for the terminal, or None if unavailable."""
    try:
        import qrcode
    except ImportError:
        return None
    try:
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        buf = io.StringIO()
        qr.print_ascii(out=buf, invert=True)
        return buf.getvalue()
    except Exception:
        return None


def qr_data_uri(url: str) -> str | None:
    """
    Render `url` as an SVG QR code in a data URI.

    Returned as a data URI rather than raw markup so the page can drop it into
    an <img src>, where SVG cannot run script — inlining the markup instead
    would hand the document an injection point for no benefit.
    """
    try:
        import qrcode
        import qrcode.image.svg
    except ImportError:
        return None
    try:
        img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=1)
        buf = io.BytesIO()
        img.save(buf)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/svg+xml;base64,{encoded}"
    except Exception:
        return None
