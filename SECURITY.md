# Security Policy

The SPIDER_CTRL project takes the security of its users and software very seriously. Because SPIDER_CTRL enables remote control of a host computer's input, processes, and terminal over a local network, maintaining a secure design is paramount.

---

## Supported Versions

Only the latest release on the `main` branch receives security updates.

| Version | Supported          |
| ------- | ------------------ |
| >= 1.0  | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you believe you have discovered a vulnerability or security risk in SPIDER_CTRL:

1. **GitHub Private Vulnerability Reporting (Preferred)**:
   Navigate to the **Security** tab of this repository on GitHub and click **"Report a vulnerability"**. This allows for coordinated, private communication and patch testing before public disclosure.

2. **Email Disclosure**:
   If private reporting is unavailable, please email **muneebkhan08304@gmail.com** with:
   - A clear description of the vulnerability and potential impact.
   - Detailed steps to reproduce the issue or proof-of-concept (PoC) code.
   - Any proposed mitigations or fixes.

### Response Timeline
- **Initial acknowledgment**: Within 48 hours.
- **Triage & severity assessment**: Within 5 business days.
- **Fix and public advisory**: Coordinated based on severity and release schedule.

---

## Security Model & Design Principles

SPIDER_CTRL is designed around several fundamental security rules:

1. **No Third-Party Cloud Relays**:
   All communication happens directly between the mobile device and the host PC over the local network (LAN) or loopback interface. No control traffic or screen stream passes through an external server.

2. **Guarded Pairing Flow**:
   The `/pair` endpoint is restricted to local loopback (`127.0.0.1` / `::1`). External network devices cannot query or generate pairing tokens without physical or authenticated access on the host.

3. **Per-Device Auth Tokens**:
   All WebSocket control frames and sensitive endpoints require a cryptographically generated pairing token. Invalid or missing tokens immediately terminate the connection.

4. **Installer Integrity**:
   Installers (`install.sh` and `install.ps1`) only pull dependencies from verified package indices (PyPI, npm) and run in isolated virtual environments (`venv`).

---

## Responsible Disclosure

We appreciate the efforts of the security research community. We kindly ask that you:
- Give us reasonable time to investigate and resolve an issue before publishing details.
- Avoid accessing, destroying, or modifying user data during research.
- Act in good faith to maintain privacy and stability for all users.
