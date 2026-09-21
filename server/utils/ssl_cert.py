"""
Self-signed SSL certificate generator.
Creates cert.pem + key.pem so the server can serve HTTPS/WSS, regenerating
them whenever the local IP changes (the SAN has to match).

Wired into server.py — enable TLS by setting the SPIDER_CTRL_TLS=1
environment variable. See the README for details.
"""

import datetime
import ipaddress
import json
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

CERT_DIR = Path(__file__).parent.parent / "certs"
CERT_FILE = CERT_DIR / "cert.pem"
KEY_FILE = CERT_DIR / "key.pem"
META_FILE = CERT_DIR / "cert_meta.json"


def _utcnow() -> datetime.datetime:
    """Naive UTC timestamp (what x509 builders expect)."""
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _needs_regeneration(local_ip: str) -> bool:
    """Check if we need a new cert (missing files or IP changed)."""
    if not CERT_FILE.exists() or not KEY_FILE.exists():
        return True
    if META_FILE.exists():
        try:
            meta = json.loads(META_FILE.read_text())
            if meta.get("ip") != local_ip:
                return True
        except Exception:
            return True
    else:
        return True
    return False


def ensure_ssl_certs(local_ip: str) -> tuple[str, str]:
    """
    Return (cert_path, key_path), generating a self-signed certificate
    if one doesn't exist or the IP has changed.
    """
    if not _needs_regeneration(local_ip):
        return str(CERT_FILE), str(KEY_FILE)

    CERT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate RSA private key
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Build certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "SPIDER_CTRL Server"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SPIDER_CTRL"),
    ])

    san_entries = [
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]

    # Add the actual local IP
    try:
        san_entries.append(x509.IPAddress(ipaddress.IPv4Address(local_ip)))
    except ValueError:
        pass

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_utcnow())
        .not_valid_after(_utcnow() + datetime.timedelta(days=825))
        .add_extension(
            x509.SubjectAlternativeName(san_entries),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Write key
    KEY_FILE.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    # Write cert
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))

    # Write metadata
    META_FILE.write_text(json.dumps({"ip": local_ip}))

    print(f"  🔐  SSL certificate generated for {local_ip}")

    return str(CERT_FILE), str(KEY_FILE)
