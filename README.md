<p align="center">
  <img src="assets/hero-banner.jpg" alt="SPIDER_CTRL — Control your computer from your phone" width="100%">
</p>

<h1 align="center">🕷️ SPIDER_CTRL</h1>

<p align="center">
  <strong>Turn your smartphone into a powerful remote control for your computer.</strong><br>
  Touchpad · Keyboard · Live Screen Streaming · Terminal · Process Manager · File Browser
</p>

<p align="center">
  <a href="#-quick-start-guide"><img src="https://img.shields.io/badge/Get_Started-00C853?style=for-the-badge&logo=rocket&logoColor=white" alt="Get Started"></a>
  <a href="#-features-overview"><img src="https://img.shields.io/badge/Features-2196F3?style=for-the-badge&logo=star&logoColor=white" alt="Features"></a>
  <a href="#-real-world-use-cases"><img src="https://img.shields.io/badge/Use_Cases-FF9800?style=for-the-badge&logo=lightbulb&logoColor=white" alt="Use Cases"></a>
  <a href="#-api-reference"><img src="https://img.shields.io/badge/API_Docs-9C27B0?style=for-the-badge&logo=book&logoColor=white" alt="API Docs"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Next.js-14-000000?logo=next.js&logoColor=white" alt="Next.js 14">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React 18">
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/WebRTC-333333?logo=webrtc&logoColor=white" alt="WebRTC">
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/PWA-5A0FC8?logo=pwa&logoColor=white" alt="PWA">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue" alt="Platform">
</p>

<p align="center">
  <em>No cloud. No account. No agent phoning home. Your phone talks directly to your computer over your own Wi-Fi.</em>
</p>

---

## 📖 Table of Contents

- [Why SPIDER_CTRL?](#-why-spider_ctrl)
- [Features Overview](#-features-overview)
- [Live App Interface Gallery](#-live-app-interface-gallery)
- [Real-World Use Cases](#-real-world-use-cases)
- [Architecture](#-architecture)
- [Pairing & Authentication](#-pairing--authentication)
- [Granting Input Permission](#-granting-input-permission)
- [Quick Start Guide](#-quick-start-guide)
- [Detailed Installation Guide](#-detailed-installation-guide)
- [Connecting Your Phone](#-connecting-your-phone)
- [Install as an App (PWA)](#-install-as-an-app-pwa)
- [Enabling HTTPS/TLS](#-enabling-httpstls)
- [Deploying the Frontend to Vercel](#-deploying-the-frontend-to-vercel)
- [Platform Support Matrix](#-platform-support-matrix)
- [Configuration Reference](#-configuration-reference)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Security Model](#-security-model)
- [Uninstalling](#-uninstalling)
- [Testing & Self-Check](#-testing--self-check)
- [Troubleshooting](#-troubleshooting)
- [Development Guide](#-development-guide)
- [Contributing](#-contributing)
- [FAQ](#-frequently-asked-questions)
- [License](#-license)

---

## 💡 Why SPIDER_CTRL?

Most remote desktop solutions are overkill, require installing software on both devices, or route your data through cloud servers you don't control.

**SPIDER_CTRL is different:**

| | SPIDER_CTRL | TeamViewer / AnyDesk | Chrome Remote Desktop |
|---|:---:|:---:|:---:|
| **Requires account** | ❌ No | ✅ Yes | ✅ Yes |
| **Cloud relay** | ❌ Direct LAN | ✅ Cloud servers | ✅ Google servers |
| **Install on phone** | ❌ Just a browser | ✅ App required | ✅ App required |
| **Open source** | ✅ MIT | ❌ Proprietary | ❌ Proprietary |
| **Works offline** | ✅ LAN only | ❌ Needs internet | ❌ Needs internet |
| **Data stays local** | ✅ Always | ❌ Routed through cloud | ❌ Routed through cloud |
| **Custom automation** | ✅ WebSocket API | ❌ | ❌ |
| **Latency** | < 10ms (LAN) | 50–200ms | 50–150ms |

**Zero install on the phone.** Open a URL in your mobile browser — that's it. Install as a PWA for a native-app experience with its own icon and no browser chrome.

**Privacy first.** All traffic stays on your local network. No cloud relay, no telemetry, no account. You can verify this — the source code is right here.

---

## ✨ Features Overview

<p align="center">
  <img src="assets/features-showcase.jpg" alt="SPIDER_CTRL Feature Showcase — Touchpad, Keyboard, Screen Stream, Terminal, Volume Controls, File Browser" width="100%">
</p>

The interface has **five tabs** across the bottom: **PAD**, **KEYS**, **STRM**, **TOOLS**, **SYS**.

---

### 📱 Live App Interface Gallery

Direct screen captures from the live SPIDER_CTRL mobile client running on a phone connected to the host system over local Wi-Fi:

<p align="center">
  <img src="assets/screenshots/01-touchpad.jpg" width="23%" alt="Touchpad Control">
  &nbsp;
  <img src="assets/screenshots/02-keyboard.jpg" width="23%" alt="Virtual Keyboard & Macros">
  &nbsp;
  <img src="assets/screenshots/05-media.jpg" width="23%" alt="Circular Volume Dial & Media">
  &nbsp;
  <img src="assets/screenshots/06-terminal.jpg" width="23%" alt="Remote Shell Terminal">
</p>
<p align="center">
  <sub><strong>Left to Right:</strong> 1. Multi-Touch Trackpad · 2. Virtual Keyboard & Macros · 3. Volume Dial & Media Transport · 4. Remote Shell Terminal</sub>
</p>

<p align="center">
  <img src="assets/screenshots/07-processes.jpg" width="23%" alt="Real-time Process Manager">
  &nbsp;
  <img src="assets/screenshots/08-files.jpg" width="23%" alt="Remote Filesystem Explorer">
  &nbsp;
  <img src="assets/screenshots/04-apps.jpg" width="23%" alt="Cross-platform App Launcher">
  &nbsp;
  <img src="assets/screenshots/10-power.jpg" width="23%" alt="Power & System Management">
</p>
<p align="center">
  <sub><strong>Left to Right:</strong> 5. Real-Time Process Manager · 6. File Browser · 7. Quick App Launcher · 8. Power & System Controls</sub>
</p>

---

### 🖱️ PAD — Multi-Touch Trackpad

A responsive trackpad that mirrors laptop-grade gestures on your phone screen.

| Gesture | Action |
| --- | --- |
| One finger drag | Move the cursor |
| One finger tap | Left click |
| Two finger drag | Scroll (vertical **and** horizontal) |
| Two finger tap | Right click |
| Three finger tap | Middle click |

- Dedicated `L_CLICK` / middle / `R_CLICK` buttons for precision work
- Relative movement — works regardless of screen dimensions
- Configurable sensitivity (`SENSITIVITY` in `Touchpad.tsx`, default 1.8)
- Jump re-anchoring prevents cursor teleportation when lifting and re-placing fingers
- Peak finger detection for accurate gesture recognition

<p align="center">
  <img src="assets/screenshots/01-touchpad.jpg" width="280" alt="PAD — Multi-Touch Trackpad with click buttons and gesture guide">
</p>

### ⌨️ KEYS — Virtual Keyboard

- **Live text input** — every character streams instantly to the host
- **Unicode support** — emoji, accents, CJK characters auto-route through clipboard
- **Modifier keys** — Esc, Tab, Ctrl, Alt, Win/⌘, Shift, arrows
- **Function row** — F1 through F12
- **One-tap macros** — Copy, Paste, Cut, Undo, Select All, Alt+Tab, Alt+F4, Win+D, Ctrl+Shift+Esc, PrintScreen
- **macOS-aware** — `Ctrl` and `Win` automatically remap to `Command` on macOS hosts

<p align="center">
  <img src="assets/screenshots/02-keyboard.jpg" width="280" alt="KEYS — Virtual Keyboard with modifiers and function keys">
</p>

### 🖥️ STRM — Live Screen Streaming

Real-time desktop streaming via **WebRTC** — not screenshot polling, real video.

| Preset | Resolution | FPS | Target Bitrate |
| --- | --- | --- | --- |
| 🟢 Low | 640 × 360 | 15 | 500 kbps |
| 🟡 Medium | 960 × 540 | 24 | 1200 kbps |
| 🟠 High | 1280 × 720 | 30 | 2500 kbps |
| 🔴 Ultra | 1920 × 1080 | 30 | 4000 kbps |

- **Adaptive quality** — auto-adjusts based on real-time network RTT measurements
- **Live stats overlay** — latency, FPS, resolution, bitrate at a glance
- **Fullscreen** with landscape orientation lock on mobile
- **Aspect-ratio preserving** — 16:10, 4:3, and portrait monitors stream undistorted
- **Auto-reconnect** — up to 5 retries if the stream drops
- **Multi-viewer** — multiple phones can stream simultaneously with independent quality

<p align="center">
  <img src="assets/screenshots/03-stream.jpg" width="280" alt="STRM — WebRTC Screen Streaming Interface">
</p>

### 🧰 TOOLS — Six Powerful Utilities

Six sub-tabs: **SRCH**, **APPS**, **MEDIA**, **SHELL**, **PROC**, **FS**.

#### 🔍 SRCH — Google Search & URL

Open any URL or run a Google search directly in the host's default browser. Recent entries are remembered locally. Bare hostnames get `https://` prepended automatically.

<p align="center">
  <img src="assets/screenshots/09-search.jpg" width="280" alt="SRCH — Google Search and URL launcher">
</p>

#### 📱 APPS — App Launcher

A searchable grid of **30+ preconfigured apps** per platform:

- **Windows**: Notepad, Calculator, Chrome, VS Code, Spotify, Discord, Steam, Terminal, Office apps, and more
- **macOS**: Finder, Safari, Chrome, iTerm, Activity Monitor, System Settings, Music, and more
- **Linux**: Nautilus, Firefox, Chrome, gnome-terminal, VS Code, VLC, LibreOffice, and more

Anything not in the list can be launched by typing its command directly.

<p align="center">
  <img src="assets/screenshots/04-apps.jpg" width="280" alt="APPS — Cross-Platform App Launcher Grid">
</p>

#### 🔊 MEDIA — Volume & Media Controls

Circular volume dial with ±5% step controls and mute toggle. Transport controls for play/pause, next, previous, and stop — emits real media keys, works with Spotify, YouTube, VLC, or any focused app.

<p align="center">
  <img src="assets/screenshots/05-media.jpg" width="280" alt="MEDIA — Circular Volume Dial and Transport Controls">
</p>

#### 💻 SHELL — Remote Terminal

A full shell on the host machine:

- **Persistent working directory** — `cd` sticks between commands
- **Command history** — ↑ / ↓ recall (last 50 commands)
- **Separated output** — stdout and stderr rendered distinctly, with exit codes
- **Timeouts** — 30s default (120s max), 64KB output cap per stream
- **Home-relative paths** — `C:\Users\you\src` displays as `~/src`

<p align="center">
  <img src="assets/screenshots/06-terminal.jpg" width="280" alt="SHELL — Remote Command Shell Terminal">
</p>

#### ⚙️ PROC — Process Manager

Live process table refreshing every 5 seconds:

- Sort by memory, CPU, name, or PID
- Filter by name
- Per-process detail: executable path, command line, thread count, user, start time
- Graceful terminate (SIGTERM) or force kill (SIGKILL)
- System summary: CPU %, core count, RAM used/total
- PIDs 0 and 4 are protected from being killed

<p align="center">
  <img src="assets/screenshots/07-processes.jpg" width="280" alt="PROC — Real-Time Process Manager and System Metrics">
</p>

#### 📁 FS — File Browser

Read-only filesystem browser:

- Drive and mount-point picker (`C:\`, `D:\` on Windows; `/`, `/home`, `/mnt` on Unix)
- Folders first, then alphabetical; sizes and modified timestamps
- Per-extension icons for code, documents, images, video, audio, and archives
- Symlinks flagged; hidden and system files filtered by default

> **Safe by design** — file contents are never transmitted. Nothing can be created, moved, or deleted.

<p align="center">
  <img src="assets/screenshots/08-files.jpg" width="280" alt="FS — Read-Only File System Explorer">
</p>

### ⚡ SYS — Power & System Controls

Shutdown, Restart, Sleep, Lock Screen, and Log Out — each behind a confirmation step. Works on **Windows, macOS, and Linux**. The host's OS, hostname, CPU, RAM, and battery level are shown alongside.

<p align="center">
  <img src="assets/screenshots/10-power.jpg" width="280" alt="SYS — Power Controls with Two-Step Confirmation">
</p>

### 📋 Clipboard Sync

Read and write the host clipboard remotely:
- **Windows**: PowerShell
- **macOS**: `pbcopy` / `pbpaste`
- **Linux**: `wl-clipboard`, `xclip`, or `xsel`

### 📡 Auto-Discovery

The server broadcasts a UDP beacon on port 8766 every 2 seconds. When you open the UI from the same network, the app can auto-detect and connect — no IP to type.

---

## 🌍 Real-World Use Cases

<p align="center">
  <img src="assets/use-cases.jpg" alt="SPIDER_CTRL Real-World Use Cases — Presentations, Media Center, IT Support, Accessibility" width="100%">
</p>

### 🎤 Presentations & Lectures

Control your presentation slides wirelessly from your phone. Walk around the room while advancing slides, switching apps, or adjusting volume — no need for a \$50 Logitech clicker.

> **Example workflow:** Stand at the podium → open SPIDER_CTRL on your phone → use the trackpad to advance PowerPoint slides → switch to a demo app → adjust volume for a video — all from your phone.

### 🎬 Home Media Center

Turn your HTPC or connected laptop into a media center controlled from the couch. Browse media files, launch VLC/Spotify, adjust volume, and control playback without getting up.

> **Example workflow:** Couch → launch Spotify from the app launcher → control volume with the media dial → skip tracks → search for a YouTube video → stream it on the big screen.

### 🖥️ IT Support & Server Monitoring

Monitor server processes, check system resources, kill hanging processes, and execute diagnostic commands — all from your phone while walking between server racks.

> **Example workflow:** Walk to server rack → open Process Manager → sort by CPU usage → identify the runaway process → kill it → run a diagnostic command in the terminal → verify the fix.

### ♿ Accessibility & Alternative Input

Use your phone as an adaptive input device when a traditional mouse or keyboard isn't practical. The touchpad works as a high-precision pointer, and the virtual keyboard handles full text input.

### 🏠 Remote Desktop for Home Use

Your computer is in the office, but you need to check something while you're in the kitchen. No need to walk back — pull out your phone, stream the screen, and handle it remotely.

### 🎮 Gaming & Streaming Setup

Control OBS scene switching, adjust audio levels, or manage your streaming overlay from your phone while gaming. Keep your hands on the keyboard and mouse while using the phone for auxiliary controls.

### 👨‍💻 Developer Workflow

Run build commands, check logs, restart services, or browse project files from your phone while stepping away from your desk. The remote terminal supports full command execution.

> **Example workflow:** Step away from desk → run `npm run build` in the terminal → check the output → browse the `/dist` folder in the file browser → verify the build.

---

## 🏗️ Architecture

<p align="center">
  <img src="assets/architecture-diagram.jpg" alt="SPIDER_CTRL Architecture — Phone communicates with Host PC via WebSocket and WebRTC over local Wi-Fi" width="100%">
</p>

### Technology Stack

| Layer | Technology | Runs On |
| --- | --- | --- |
| **UI Framework** | Next.js 14 (App Router) + React 18 + TypeScript | Phone browser |
| **Styling** | Tailwind CSS + Framer Motion, JetBrains Mono | Phone browser |
| **Control Channel** | WebSocket (JSON request/response) | LAN |
| **Video Channel** | WebRTC (aiortc ⇄ browser), H.264/VP8 | LAN |
| **Server** | FastAPI + Uvicorn (Python) | Host PC |
| **Input Automation** | pyautogui | Host PC |
| **Screen Capture** | mss + NumPy + PyAV | Host PC |
| **System Control** | psutil, pycaw (Win) / osascript (Mac) / pactl (Linux) | Host PC |

### Why Two Channels?

**WebSocket** for control — small, ordered messages that need replies (mouse moves, key presses, shell commands).

**WebRTC** for video — continuous high-bandwidth stream that tolerates packet loss, with built-in NAT traversal and congestion control.

### One Server, Two Jobs

The Python server both handles API requests AND serves the frontend as static files. A phone on the same network just browses to `http://<pc-ip>:8765` — nothing else to deploy.

> 📐 **[ARCHITECTURE.md](ARCHITECTURE.md)** goes deeper: the browser rules that
> shaped the design, why there is no cloud broker, the pairing threat model,
> connection sequence diagrams, and the full cost/licence breakdown.

---

## 🔑 Pairing & Authentication

Every device pairs **once**. Pairing hands the phone a 256-bit token that it
stores and reuses, so this only happens the first time.

### The flow

```
┌─ On the PC ────────────────────────────────────────────────┐
│  1. Open the site (deployed, or http://localhost:8765)     │
│  2. Not installed? Copy the one-line install command       │
│  3. The server starts and the page shows a QR code         │
└────────────────────────────────────────────────────────────┘
                              │
┌─ On the phone ─────────────────────────────────────────────┐
│  4. Scan the QR with the camera, open the link             │
│  5. Paired and connected — nothing typed                   │
└────────────────────────────────────────────────────────────┘
```

The server prints the **same QR code in its terminal**, so the flow works even
if the setup page can't reach the server (Safari blocks page→localhost requests).

### No camera?

Browse to the address the server printed and enter the six-character pairing
code shown on the PC. The code **works once** and **expires after 10 minutes** —
restart the server for a fresh one.

### Install one-liners

The connector page shows the right command for your OS:

```powershell
irm https://spider-ctrl.vercel.app/install.ps1 | iex
```

```bash
curl -fsSL https://spider-ctrl.vercel.app/install.sh | sh
```

Each clones the repo to `~/.spider-ctrl`, builds the UI, creates the virtualenv,
opens the firewall port where it can, and starts the server. Re-running updates
in place. Requires Python 3.9+, Node 18+ and git.

### Managing pairings

| Task | How |
| --- | --- |
| Pair a new device | Scan the QR, or enter the pairing code |
| Unpair one device | Tap **forget this pc** in the app's connection panel |
| Unpair *everything* | `POST /pair/rotate` from the PC, or delete `server/config/pairing.json`. Devices that are connected right now are kicked immediately |

The token lives in `server/config/pairing.json` (gitignored, `chmod 600` on
POSIX). It is stripped from the phone's address bar immediately after it is
stored, so it never lingers in history or screenshots.

---

## 👆 Granting Input Permission

> [!IMPORTANT]
> **macOS and Linux need one permission before the trackpad and keyboard do
> anything.** Without it the phone still pairs and connects, every button still
> lights up, and *nothing moves* — the OS discards the synthetic events and
> pyautogui does not report an error.

SPIDER_CTRL detects this now. The server prints a warning on startup and the
phone shows an amber **INPUT BLOCKED ON THE PC** banner with the exact fix.

### macOS

1. **System Settings → Privacy & Security → Accessibility**
2. Switch **ON** the app you start the server from — **Terminal**, **iTerm**,
   or whichever app you launch it in
3. **Quit the server and start it again** — the permission is only read when a
   process starts

> macOS grants Accessibility to the *responsible* process, which for a
> command-line server is the terminal app, **not** the Python binary. Adding
> `python3` alone usually will not work. If you launch the server some other
> way (a LaunchAgent, a bundled app), add the interpreter the warning prints.

Screen streaming additionally needs **Screen Recording** for the same app.

### Linux

pyautogui drives X11. A pure **Wayland** session blocks synthetic input
outright — log into an Xorg session instead. The server reports this too.

### Windows

Nothing to grant. If the target window ignores input it is usually running
elevated, so run the server as administrator too.

### Checking it

```bash
curl -s http://localhost:8765/health | grep input_ok
```

`"input_ok": true` means the OS will accept input. The phone can also re-check
from the banner without restarting anything.

---

## 🚀 Quick Start Guide

Get running in under 2 minutes.

### Prerequisites

| Component | Requirement |
| --- | --- |
| **Host PC** | Python 3.10+ (3.11+ recommended) |
| **Frontend Build** | Node.js 18+ and npm |
| **Operating System** | Windows 10/11, macOS 11+, or Linux (X11/Wayland) |
| **Phone** | Any modern browser (Chrome, Safari, Firefox, Edge) |
| **Network** | Same Wi-Fi, LAN, or hotspot |

### One-Command Start

<details>
<summary><b>🪟 Windows</b></summary>

```bat
git clone https://github.com/muneebkhan08/test_mob_ctrl.git
cd test_mob_ctrl
start-server.bat
```

The batch file handles venv creation, dependency installation, frontend build, and server launch automatically.

</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
git clone https://github.com/muneebkhan08/test_mob_ctrl.git
cd test_mob_ctrl
chmod +x start-server.sh
./start-server.sh
```

> **First time on macOS?** You'll need to grant **Accessibility** and **Screen Recording** permissions:
> System Settings → Privacy & Security → Accessibility → add Terminal/Python.
> System Settings → Privacy & Security → Screen Recording → add Terminal/Python.

</details>

<details>
<summary><b>🐧 Linux</b></summary>

```bash
git clone https://github.com/muneebkhan08/test_mob_ctrl.git
cd test_mob_ctrl
chmod +x start-server.sh
./start-server.sh
```

> **Note:** X11 works out of the box. Wayland restricts synthetic input — run under XWayland or an X11 session for full functionality.

</details>

### You Should See

```
════════════════════════════════════════════════════════
  🖥️  SPIDER_CTRL Server v1.0.0
  🔌  WebSocket  →  ws://192.168.1.42:8765/ws
  🎥  WebRTC     →  /webrtc/offer
  📡  UDP Disco   →  port 8766
  🔒  TLS         →  disabled (set SPIDER_CTRL_TLS=1)
  💻  Platform    →  Windows 10
════════════════════════════════════════════════════════

  📱  Scan this with your phone's camera:

  █▀▀▀▀▀▀▀█▀█▀█▀▀▀▀█▀▀▀█▀▀▀███▀██▀▀▀▀▀▀▀█
  █ █▀▀▀█ █▀█ ▄████▄▀█▄█▀ █▄ █▀██ █▀▀▀█ █
  █ █   █ ██ ▄█▄█ ▄ ▀  ▄▄█▄▄ ▀█ █ █   █ █
  █ ▀▀▀▀▀ █ █ █▀▄ ▄▀█▀█ ▄ █ ▄▀█▀█ ▀▀▀▀▀ █
  █▀█▀███▀▀██▀▄▀███▀▀ ███▄▄▄██▀▀██▀██▀█▀█
                  … (full QR) …
  ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

  🔗  Or open on phone →  http://192.168.1.42:8765
  🔑  Pairing code     →  8PB-5P8
  🖥️  Setup screen     →  http://localhost:8765/
════════════════════════════════════════════════════════
```

**Scan the QR with your phone's camera and open the link. That's it** — the QR
carries the pairing token, so the phone pairs and connects in one step.

> **First run on macOS or Linux?** Check everything is wired up before you
> rely on it:
>
> ```bash
> cd server && venv/bin/python selftest.py
> ```
>
> Mouse and keyboard fail until you grant input permission — see
> [Granting Input Permission](#-granting-input-permission).

The setup screen also opens in your browser automatically, showing the same QR
at a comfortable size.

---

## 📥 Detailed Installation Guide

Step-by-step for all platforms.

### Step 1: Clone the Repository

```bash
git clone https://github.com/muneebkhan08/test_mob_ctrl.git
cd test_mob_ctrl
```

### Step 2: Build the Frontend

```bash
cd frontend
npm install
npm run build     # Creates static export in frontend/out/
cd ..
```

> The `npm run build` command produces a static export of the Next.js app. This is what the Python server serves to your phone.

### Step 3: Set Up the Python Server

```bash
cd server

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run the Server

```bash
python server.py
```

### Step 5: Connect Your Phone

1. Make sure your phone is on the **same Wi-Fi network** as your computer
2. **Scan the QR code** the server prints on startup — the setup screen also
   opens in your browser automatically with the same code
3. That's it. The QR carries the pairing token, so the phone pairs and connects
   in one step with nothing to type

No camera? Open the address the server prints (e.g. `http://192.168.1.42:8765`)
and enter the six-character pairing code shown on the PC.

### Updating

```bash
cd test_mob_ctrl
git pull
cd frontend && npm install && npm run build && cd ..
cd server && pip install -r requirements.txt && cd ..
```

---

## 📲 Connecting Your Phone

Every device has to **pair once** before it can control the PC. Pairing hands
the phone a token that it stores and reuses, so this only happens the first time.

### Method 1: Scan the QR (Simplest)

Both devices on the same router. Point the phone's camera at the QR code — in
the server's terminal, or on the setup screen that opens at
`http://localhost:8765`. Open the link and you're connected.

### Method 1b: Pairing Code

If the camera isn't an option, browse to the address the server printed and type
the six-character code from the PC. The code works once and expires after ten
minutes; restart the server for a fresh one.

### Method 2: PC as Hotspot

1. **Windows:** Settings → Network → Mobile Hotspot → On
   **macOS:** System Settings → General → Sharing → Internet Sharing
2. Connect the phone to that hotspot
3. Use the host's hotspot IP (usually `192.168.137.1` on Windows)

### Method 3: Phone as Hotspot

1. Enable the hotspot on your phone
2. Connect the PC to it
3. Start the server and use whichever IP it prints

### Finding the Host IP Manually

```bash
ipconfig                      # Windows
ifconfig | grep "inet "       # macOS
hostname -I                   # Linux
```

---

## 📱 Install as an App (PWA)

SPIDER_CTRL is a Progressive Web App — install it on your phone for a native-app experience:

**iOS (Safari):**
1. Open the server URL in Safari
2. Tap the **Share** button (⬆️)
3. Tap **Add to Home Screen**
4. Tap **Add**

**Android (Chrome):**
1. Open the server URL in Chrome
2. Tap the **⋮** menu
3. Tap **Add to Home screen** or **Install app**

Once installed, it launches fullscreen with no browser chrome, its own icon, and the dark theme applied to the status bar.

---

## 🔐 Enabling HTTPS/TLS

SPIDER_CTRL supports optional TLS encryption for secure connections:

```bash
# Enable TLS with a single environment variable
SPIDER_CTRL_TLS=1 python server.py
```

**What happens:**
1. A self-signed SSL certificate is auto-generated with your local IP in the SAN
2. The certificate regenerates automatically when your IP changes
3. The server starts on `https://` and `wss://` instead of plain HTTP
4. You'll need to accept the self-signed certificate warning on your phone (once per IP change)

**On Windows:**

```bat
set SPIDER_CTRL_TLS=1
python server.py
```

> **Note:** TLS encrypts the channel but doesn't authenticate clients. For trusted networks, plain HTTP is fine. Enable TLS if you want encryption on the wire.

---

## ☁️ Deploying the Frontend to Vercel

Optional. Hosting the UI on Vercel gives you a stable URL to bookmark instead of a changing IP.

1. Push the repo to GitHub
2. Vercel → **Add New** → **Project** → import the repo
3. **Set Root Directory to `frontend`** (critical — the repo root has no `package.json`)
4. Framework preset: `Next.js`. Leave all other settings at defaults.
5. Deploy

**How it works:** The Vercel-hosted page acts as a launcher. You type the host IP, tap **Go**, and it redirects to `http://<ip>:8765` where the server handles everything same-origin. The last IP is remembered.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the click-by-click walkthrough.

---

## 💻 Platform Support Matrix

| Feature | Windows | macOS | Linux |
| --- | :---: | :---: | :---: |
| Mouse / Keyboard | ✅ | ✅ ¹ | ✅ ² |
| Screen Streaming | ✅ | ✅ ¹ | ✅ |
| Terminal | ✅ | ✅ | ✅ |
| Process Manager | ✅ | ✅ | ✅ |
| File Browser | ✅ | ✅ | ✅ |
| App Launcher | ✅ | ✅ | ✅ |
| Power Controls | ✅ | ✅ | ✅ |
| Volume | ✅ pycaw | ✅ osascript | ✅ pactl |
| Media Keys | ✅ | ✅ | ⚠️ ³ |
| Clipboard | ✅ | ✅ | ✅ ⁴ |

> ¹ macOS needs **Accessibility** and **Screen Recording** permissions for the terminal or Python binary: System Settings → Privacy & Security.
>
> ² X11 works out of the box. Wayland restricts synthetic input; run under XWayland or an X11 session.
>
> ³ Media keys depend on the desktop environment honouring XF86 key symbols.
>
> ⁴ Linux needs `wl-clipboard`, `xclip`, or `xsel` installed.

`pycaw` and `comtypes` are marked `sys_platform == "win32"` in `requirements.txt`, so `pip install -r requirements.txt` is safe on all platforms.

---

## ⚙️ Configuration Reference

### Server Configuration

Constants at the top of `server/server.py`:

| Constant | Default | Description |
| --- | --- | --- |
| `SERVER_PORT` | `8765` | HTTP + WebSocket port |
| `UDP_PORT` | `8766` | Discovery broadcast port |
| `BROADCAST_INTERVAL` | `2` | Seconds between UDP beacons |

### Environment Variables

| Variable | Values | Description |
| --- | --- | --- |
| `SPIDER_CTRL_TLS` | `1`, `true`, `yes` | Enable HTTPS/WSS with auto-generated self-signed certificates |
| `SPIDER_CTRL_ORIGINS` | Comma-separated origins | Hosted copies of the UI allowed to read `/pair`. Default: `https://spider-ctrl.vercel.app` |
| `SPIDER_CTRL_NO_BROWSER` | `1`, `true`, `yes` | Don't open the setup page on boot (headless / service installs) |

> [!WARNING]
> `SPIDER_CTRL_ORIGINS` is **exact match only** — set it to your real deployment
> URL. The `/pair` response carries the pairing token, so a wildcard here would
> let any site the user visits read it and take over the machine.

### Controller Configuration

| File | Constant | Default | Description |
| --- | --- | --- | --- |
| `controllers/terminal.py` | `DEFAULT_TIMEOUT` | 30s | Shell command timeout |
| `controllers/terminal.py` | `MAX_TIMEOUT` | 120s | Maximum allowed timeout |
| `controllers/terminal.py` | `MAX_OUTPUT_BYTES` | 64 KB | Output cap per stream |
| `controllers/screen.py` | `QUALITY_PRESETS` | see table above | WebRTC stream quality |
| `utils/pairing.py` | `CODE_TTL` | 600s | Pairing-code lifetime |
| `utils/pairing.py` | `CODE_MAX_ATTEMPTS` | 5 | Wrong guesses before the code is destroyed |
| `utils/pairing.py` | `CODE_LENGTH` | 6 | Characters in the pairing code |

### Frontend Configuration

| File | Constant | Default | Description |
| --- | --- | --- | --- |
| `Touchpad.tsx` | `SENSITIVITY` | `1.8` | Trackpad sensitivity multiplier |
| `useWebSocket.tsx` | `RECONNECT_DELAY` | 3000 ms | WebSocket reconnect interval |

### Theme Customization

Theme colours are defined in two places — change both to restyle:
- CSS variables in `app/globals.css`
- Tailwind tokens in `tailwind.config.js`

---

## 📡 API Reference

### WebSocket Protocol

**Endpoint:** `ws://<host>:8765/ws`

All frames are JSON. Request-response pairing uses an optional `id` field.

**Request format:**

```jsonc
{
  "action": "mouse_move",
  "payload": { "dx": 10, "dy": -5 },
  "id": "req_1"      // optional — include to get a reply
}
```

**Response format:**

```jsonc
{ "ok": true,  "data": { "moved": [10, -5] }, "id": "req_1" }
{ "ok": false, "error": "Process 1234 does not exist", "id": "req_1" }
```

> **Performance tip:** Fire-and-forget messages (cursor movement, key presses) omit `id` and get no reply, keeping the trackpad smooth at 60+ events/second.

### Action Reference

<details>
<summary><b>🖱️ Mouse Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `mouse_move` | `{dx, dy}` | Relative cursor move |
| `mouse_click` | `{button}` — `left`\|`right`\|`middle` | Click |
| `mouse_double_click` | — | Double click |
| `mouse_right_click` | — | Right click |
| `mouse_scroll` | `{dx, dy}` | Scroll both axes |
| `mouse_drag_start` | — | Press and hold |
| `mouse_drag_move` | `{dx, dy}` | Move while held |
| `mouse_drag_end` | — | Release |

</details>

<details>
<summary><b>⌨️ Keyboard Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `key_press` | `{key}` | Press one key |
| `key_combo` | `{keys: [...]}` | Chord, e.g. `["ctrl","shift","esc"]` |
| `key_type` | `{text}` | Type a string (unicode via clipboard) |

</details>

<details>
<summary><b>⚡ Power Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `power_shutdown` | `{delay?}` | Shut down after `delay` seconds |
| `power_restart` | `{delay?}` | Restart |
| `power_sleep` | — | Suspend |
| `power_lock` | — | Lock the screen |
| `power_logout` | — | Log the user out |

</details>

<details>
<summary><b>📱 App & Search Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `app_open` | `{name}` or `{path}` | Launch by friendly name or command |
| `app_list` | — | Quick-launch names + running processes |
| `app_close` | `{name}` or `{pid}` | Terminate |
| `google_search` | `{query}` | Search in the default browser |
| `url_open` | `{url}` | Open a URL |

</details>

<details>
<summary><b>🔊 Volume & Media Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `volume_get` | — | `{volume, muted}` |
| `volume_set` | `{level}` | Set 0–100 |
| `volume_up` / `volume_down` | `{step?}` | Step, default 5 |
| `volume_mute` | — | Toggle mute |
| `media_play_pause` | — | Play / pause |
| `media_next` / `media_prev` | — | Track change |
| `media_stop` | — | Stop |

</details>

<details>
<summary><b>💻 Terminal Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `terminal_execute` | `{command, timeout?}` | `{stdout, stderr, exit_code, cwd}` |
| `terminal_cwd` | — | Current directory |
| `terminal_set_cwd` | `{path}` | Change directory |
| `terminal_reset` | — | Back to home |

</details>

<details>
<summary><b>⚙️ Process Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `process_list` | `{sort_by?, limit?, search?}` | Processes + system summary |
| `process_detail` | `{pid}` | exe, cmdline, threads, user, start time |
| `process_kill` | `{pid, force?}` | SIGTERM, or SIGKILL when `force` |

</details>

<details>
<summary><b>📁 Filesystem Actions</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `fs_list` | `{path?, show_hidden?}` | Entries with metadata |
| `fs_drives` | — | Drives / mount points |
| `fs_info` | `{path}` | Single-entry detail |

</details>

<details>
<summary><b>📋 Clipboard & System Info</b></summary>

| Action | Payload | Description |
| --- | --- | --- |
| `clipboard_get` | — | `{text}` |
| `clipboard_set` | `{text}` | `{copied: true}` |
| `system_info` | — | Host, OS, CPU, RAM, battery |
| `input_status` | — | `{ok, reason, fix, binary, platform}` — whether the OS will accept synthetic input |

</details>

### HTTP Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Server status, IP, platform, active stream count, `input_ok` |
| `GET` | `/pair` | **Loopback only.** Token, QR (SVG data URI), pairing code, address |
| `POST` | `/pair/claim` | Trade a six-character code for the token — `{code}` → `{token, ip, port}` |
| `GET` | `/uninstall/plan` | **Loopback only.** What deleting *this* install would remove, with sizes. Changes nothing |
| `POST` | `/uninstall` | **Loopback only.** Deletes *this* install. Requires `{"confirm":"DELETE"}`; the server stops afterwards |
| `GET` | `/uninstall/scan` | **Loopback only.** Every SPIDER_CTRL install found (default location + any `?path=`), each with the same shape as `/uninstall/plan` |
| `POST` | `/uninstall/remove` | **Loopback only.** Deletes the install at `{"root": "...", "confirm": "DELETE"}`. Never stops the server unless `root` is its own tree |
| `POST` | `/pair/rotate` | **Loopback only.** New token; unpairs every device and disconnects any that are live. Returns `{ok, url, disconnected}` |
| `GET` | `/{path}` | Static frontend (SPA fallback to `index.html`) |

**WebSocket auth:** connect to `ws://<host>:8765/ws?t=<token>`. A missing,
wrong or rotated token is closed with code **1008** — distinct from a dropped
connection, so the client knows to re-pair instead of retrying forever.

### WebRTC Signalling API

| Method | Path | Body | Returns |
| --- | --- | --- | --- |
| `POST` | `/webrtc/offer` | `{sdp, type, quality}` | `{connection_id, sdp, type, quality}` |
| `POST` | `/webrtc/ice` | `{connection_id, candidate}` | `{ok}` |
| `POST` | `/webrtc/quality` | `{connection_id, quality}` | `{ok, quality}` |
| `POST` | `/webrtc/stop` | `{connection_id}` | `{ok}` |
| `GET` | `/webrtc/stats/{id}` | — | Connection and ICE state |

**Flow:** Browser creates offer → `POST /webrtc/offer` → server attaches screen capture track and answers → ICE candidates trickle both ways → video flows. A data channel named `stats` carries RTT reports and quality changes without HTTP round-trips.

### UDP Discovery

The server broadcasts to port **8766** every 2 seconds:

```json
{
  "service": "SPIDER_CTRL Server",
  "version": "1.0.0",
  "ip": "192.168.1.42",
  "port": 8765,
  "hostname": "DESKTOP-ABC",
  "platform": "Windows"
}
```

---

## 📁 Project Structure

```
test_mob_ctrl/
├── assets/                          # README images
├── frontend/                        # Next.js PWA (static export)
│   ├── app/
│   │   ├── page.tsx                 # Tab shell and layout
│   │   ├── layout.tsx               # Metadata, PWA manifest, icons
│   │   ├── globals.css              # Cyberpunk theme, animations
│   │   ├── hooks/
│   │   │   ├── useWebSocket.tsx     # Control channel, reconnect, req/res
│   │   │   └── useWebRTC.tsx        # Video channel, signalling, stats
│   │   └── components/
│   │       ├── PCConnector.tsx      # Desktop setup: install + pairing QR
│   │       ├── PairPrompt.tsx       # Phone: pairing-code entry
│   │       ├── InputWarning.tsx     # Warns when the OS blocks input
│   │       ├── UninstallPanel.tsx   # Danger zone: remove from this PC
│   │       ├── OtherInstalls.tsx    # Find + remove any install on the machine
│   │       ├── ConnectionBar.tsx    # Connect / redirect / status
│   │       ├── Touchpad.tsx         # Multi-touch trackpad
│   │       ├── Keyboard.tsx         # Text, keys, macros
│   │       ├── ScreenViewer.tsx     # Video surface + quality UI
│   │       ├── RemoteTerminal.tsx   # Shell emulator
│   │       ├── ProcessManager.tsx   # Process table
│   │       ├── FileBrowser.tsx      # Filesystem browser
│   │       ├── AppLauncher.tsx      # App grid
│   │       ├── GoogleSearch.tsx     # Search / URL
│   │       ├── MediaVolume.tsx      # Volume + transport
│   │       └── PowerControls.tsx    # Power actions
│   ├── public/                      # manifest.json, PWA icons
│   │   ├── install.sh               # macOS / Linux one-line installer
│   │   └── install.ps1              # Windows one-line installer
│   └── out/                         # Build output — served by the server
│
├── server/                          # FastAPI server (runs on the host)
│   ├── server.py                    # App, WS endpoint, dispatch, UDP beacon
│   ├── selftest.py                  # Health check for every subsystem
│   ├── requirements.txt             # Python dependencies with platform markers
│   ├── requirements-dev.txt         # pytest, for the test suite
│   ├── tests/
│   │   ├── test_pairing.py          # Token, code and origin-policy tests
│   │   ├── test_server_auth.py      # Route-level auth and revocation
│   │   ├── test_permissions.py      # Input-permission detection
│   │   └── test_uninstall.py        # Uninstall safety (mostly refusals)
│   ├── controllers/
│   │   ├── mouse.py                 # Move, click, scroll, drag
│   │   ├── keyboard.py              # Keys, combos, text, unicode
│   │   ├── screen.py                # Capture + WebRTC track + quality
│   │   ├── terminal.py              # Shell with persistent cwd
│   │   ├── processes.py             # List / inspect / kill
│   │   ├── filesystem.py            # Read-only browsing
│   │   ├── apps.py                  # Launch and close apps (cross-platform)
│   │   ├── power.py                 # Shutdown, restart, sleep, lock (cross-platform)
│   │   ├── volume.py                # Per-platform volume control
│   │   ├── media.py                 # Media keys
│   │   ├── clipboard.py             # Per-platform clipboard
│   │   ├── search.py                # Google / URL
│   │   └── system_info.py           # CPU, RAM, battery
│   ├── utils/
│   │   ├── pairing.py               # Tokens, pairing codes, origin policy, QR
│   │   ├── permissions.py           # Can the OS actually accept input?
│   │   ├── uninstall.py             # Removal planning + guards
│   │   ├── network.py               # LAN IP detection
│   │   └── ssl_cert.py              # Self-signed cert generator
│   ├── config/                      # Pairing token — generated, gitignored
│   └── certs/                       # Generated at runtime — gitignored
│
├── start-server.bat                 # Windows launcher
├── start-server.sh                  # macOS / Linux launcher
├── ARCHITECTURE.md                  # Design deep-dive and threat model
├── DEPLOYMENT.md                    # Vercel deployment walkthrough
└── README.md
```

---

## 🔒 Security Model

> [!IMPORTANT]
> **Every connection requires a pairing token.** An unpaired device on your
> network cannot connect, and cannot run a single command. Pairing is described
> in [Pairing & Authentication](#-pairing--authentication).

### How access is controlled

| Mechanism | What it stops |
| --- | --- |
| **256-bit token on every `/ws`**, compared with `hmac.compare_digest` | Any unpaired device, **including one on loopback** |
| **Origin port check** on the WebSocket handshake | Hostile web pages and DNS rebinding — an attacker's site is served from `:80`/`:443`, never `:8765` |
| **`/pair` is loopback-only** | Other devices on the Wi-Fi simply asking for the token |
| **Exact-match CORS allowlist** | A website you have open *reading* the token — its request comes from loopback too, so the loopback check alone is not enough |
| **Private Network Access opt-in** | Adds Chrome's own gate in front of the above |
| **Code expiry, single use, 5-attempt cap** | Brute-forcing the short pairing code |

> [!NOTE]
> WebSocket handshakes are **not** subject to CORS. That is why the token is
> required even for connections from `127.0.0.1` — without it, any page you had
> open could open a socket to the server and take over the machine.

### What a paired device can still do

Pairing is all-or-nothing. Once a device holds the token it can:

- Run arbitrary shell commands as the user running the server (`terminal_execute`)
- Kill any process that user owns (`process_kill`)
- Shut down, restart or lock the machine, with no confirmation prompt
- Browse the filesystem (names and metadata, not contents)
- Watch the screen

So treat the token like a password, and only pair devices you control.

### Remaining exposure

- The server binds `0.0.0.0` — the port is reachable from the whole subnet, even though connecting requires the token
- Traffic is plaintext by default (enable TLS with `SPIDER_CTRL_TLS=1`)
- The UDP beacon on 8766 advertises the server's presence to the subnet
- There is no per-device revocation — rotating drops **every** device (connected ones are disconnected immediately) and they all have to pair again
- There is no approval prompt on the PC; the token is the only gate

### Safe Networks

| ✅ Safe | ❌ Unsafe |
| --- | --- |
| Home Wi-Fi with WPA2/WPA3 | Café, airport, hotel Wi-Fi |
| Your own hotspot | Campus Wi-Fi with guests |
| Isolated LAN | Port forwarding to the internet |

### Hardening Checklist

- [ ] **Keep the token secret** — anyone holding it has full control; rotate with `/pair/rotate` if a device is lost
- [ ] **Run only while using it** — the UDP beacon advertises your server to the entire subnet
- [ ] **Firewall it** — allow 8765/tcp and 8766/udp on private profiles only
- [ ] **Enable TLS** — `SPIDER_CTRL_TLS=1` encrypts traffic with auto-generated certs
- [ ] **Run as unprivileged user** — don't launch from an admin/root shell
- [ ] **Don't tunnel it** — no ngrok, no Tailscale funnel, no port forwarding

**Windows firewall rules (elevated PowerShell):**

```powershell
New-NetFirewallRule -DisplayName "SPIDER_CTRL" -Direction Inbound -Protocol TCP -LocalPort 8765 -Profile Private -Action Allow
New-NetFirewallRule -DisplayName "SPIDER_CTRL Disco" -Direction Inbound -Protocol UDP -LocalPort 8766 -Profile Private -Action Allow
```

### About the Committed Certificate

The repo's first commit included a self-signed `key.pem`. Those files are no longer tracked, and `.gitignore` now covers them. They remain in git history — use `git filter-repo` to purge if needed. The practical impact is low as the key was never wired into the running server.

---

## 🧪 Testing & Self-Check

### Is my install healthy?

Run the self-test. It checks every subsystem and tells you exactly what to fix.

```bash
cd server
venv/bin/python selftest.py
```

```text
── Input control ───────────────────────────────────────
  [PASS] Mouse control
         cursor moved and was restored
  [PASS] Keyboard control
         same event path as the mouse — available
```

It is read-only apart from a one-pixel cursor nudge it puts straight back, and
it exits non-zero on failure so you can gate a script with it. Checks:

| Group | What it verifies |
| --- | --- |
| **Environment** | Python 3.9+, all 11 runtime packages, frontend actually built |
| **Pairing** | Token creates, persists and verifies; code issues; QR renders both ways |
| **Input control** | Moves the cursor and reads the position back — the real proof, not just the permission flag |
| **Screen** | Captures a frame, and warns if it comes back blank (missing Screen Recording) |
| **Media keys** | The platform's media-key mechanism is available (checked without firing a key) |
| **Controllers** | `system_info`, `filesystem`, `processes`, `clipboard`, `volume`, `terminal` each respond |
| **Network** | A real LAN address exists, and whether 8765 is free |

> Run it once after installing, and again after granting input permission.
> Mouse and keyboard are the two checks that fail on a fresh macOS install —
> see [Granting Input Permission](#-granting-input-permission).

### Automated tests

The pairing and uninstall layers decide who can drive your machine and what
gets deleted, so both ship with tests — mostly negative ones, because a
regression there is a stranger getting a shell, or your source tree going in
the bin.

```bash
cd server
venv/bin/pip install -r requirements-dev.txt
venv/bin/python -m pytest tests/ -v
```

**108 cases** across six files:

| File | Cases | Covers |
| --- | --- | --- |
| [`test_pairing.py`](server/tests/test_pairing.py) | 24 | Token lifecycle and rotation; pairing codes (no ambiguous characters, dash/case tolerance, single use, expiry, destroyed after the attempt cap); origin policy — LAN, loopback and allowlisted origins pass, hostile sites, suffix look-alikes (`…vercel.app.evil.com`), other local ports and non-HTTP schemes are rejected; QR rendering |
| [`test_server_auth.py`](server/tests/test_server_auth.py) | 23 | The routes actually apply the policy: `/pair` loopback-only and origin-gated, PNA preflight, code exchange, WebSocket auth, **an unpaired socket cannot run a command**, and rotation revoking a live connection |
| [`test_permissions.py`](server/tests/test_permissions.py) | 14 | Input detection per platform, a blocked host reported with a fix, an unverifiable check not crying wolf, and a guard against reintroducing the prompt that once segfaulted the interpreter |
| [`test_media.py`](server/tests/test_media.py) | 9 | The macOS/other-platform split for media keys, and that macOS never falls through to pyautogui — whose media keys are a silent no-op there |
| [`test_selftest.py`](server/tests/test_selftest.py) | 5 | The diagnostic itself runs to completion, reports every group, leaves nothing in an unknown state, and never fails without saying why |
| [`test_uninstall.py`](server/tests/test_uninstall.py) | 33 | Mostly refusals: a working copy's source survives, the home directory and filesystem root are rejected, targets outside the install root are skipped, every wrong spelling of the confirmation deletes nothing; plus multi-install discovery, deleting a foreign root never shuts this server down, and the psutil running-check degrades safely when it can't see a process |

---

## 🗑️ Uninstalling

The desktop setup page has a **danger zone** at the bottom with two sections:
removing *this* install, and finding every *other* one on the machine. Both
work identically on Windows, macOS and Linux — the backend resolves the
platform-specific paths, the UI just renders whatever it finds.

### Remove this install

Expand *// remove spider_ctrl from this pc*. It lists exactly what will be
deleted, with sizes, and needs you to type `DELETE` before the button does
anything. When it finishes, the server deletes its files and stops itself.

It works in one of two modes, chosen automatically:

| Mode | When | What goes |
| --- | --- | --- |
| **Full** | The tree was created by `install.sh` / `install.ps1` | The whole install directory |
| **Artifacts** | Anything else — a git clone you work in | `venv`, `node_modules`, `.next`, `out`, `config`, `certs` only. **Your source is kept.** |

The installers drop a `.spider-ctrl-install` marker, and only a tree carrying
that marker is ever removed whole. A development checkout has no marker, so
the uninstaller will not delete it even if you ask — it clears build output
and the pairing token instead.

### Find every install on this machine

Expand *// find other installs on this machine*. This is for the case the
first section doesn't cover: you ran `install.sh` / `install.ps1` more than
once, or ran an older version that predates the safety marker, and a copy is
just sitting on disk with nothing pointing at it.

It scans the same default location both installers write to — same relative
path on every OS, resolved through the account's home directory:

| OS | Default location |
| --- | --- |
| macOS / Linux | `~/.spider-ctrl` |
| Windows | `%USERPROFILE%\.spider-ctrl` |

Each result shows its size, mode, and a **RUNNING** badge if a server is
currently live in that tree — checked cross-platform via `psutil` (process
command lines and the socket listening on 8765), not `lsof`/`netstat`, so
the same code runs everywhere. Expand a result to see exactly what it would
remove, then confirm the same way as above. Deleting a *different* install
never stops the server answering your request — only deleting your own tree
does that.

Used a custom `SPIDER_CTRL_HOME` at install time? It isn't recorded anywhere
on disk, so the automatic scan can't find it — type the path into **Installed
somewhere else? Check a specific path** and it's checked the same way.

### From the command line

**This install:**

```bash
curl -s http://localhost:8765/uninstall/plan             # see what would go
curl -s -X POST http://localhost:8765/uninstall \
     -H 'Content-Type: application/json' \
     -d '{"confirm":"DELETE"}'                           # do it
```

**Every install on the machine:**

```bash
curl -s http://localhost:8765/uninstall/scan | python3 -m json.tool
```

**A specific one, or a custom path the default scan can't see:**

```bash
# macOS / Linux
curl -s "http://localhost:8765/uninstall/scan?path=$HOME/.spider-ctrl"

# Windows (PowerShell)
curl.exe -s "http://localhost:8765/uninstall/scan?path=$env:USERPROFILE\.spider-ctrl"
```

```bash
curl -s -X POST http://localhost:8765/uninstall/remove \
     -H 'Content-Type: application/json' \
     -d '{"root":"/path/from/the/scan/output","confirm":"DELETE"}'
```

All four are **loopback only** — a paired phone can enumerate or delete
nothing on your PC.

### If the server isn't running

The endpoints above need a running server. Without one, use the same guard
logic directly — this refuses a working copy's source exactly like the API
does, so it's safe to point at your dev checkout by accident:

```bash
cd server && venv/bin/python -c "
from utils import uninstall
print(uninstall.execute('DELETE'))
"
```

Or delete a known install location by hand once you're sure — the app has no
way to protect you here, since it isn't running:

```bash
# macOS / Linux
rm -rf ~/.spider-ctrl

# Windows (PowerShell)
Remove-Item -Recurse -Force "$env:USERPROFILE\.spider-ctrl"
```

### What it does not remove

- **Firewall rules** — delete the *SPIDER_CTRL Server* rule by hand if you
  added one (Windows Defender Firewall, or `ufw delete allow 8765/tcp`)
- **Node and Python themselves** — they were on your machine already
- **On Windows, the virtualenv of the install you're deleting from** — a
  running server can't delete the files it's executing out of; the result
  names the folder to remove by hand afterward. Removing a *different*,
  non-running install has no such restriction.

---

## 🔧 Troubleshooting

> **Start here:** `cd server && venv/bin/python selftest.py` names the broken
> subsystem and the fix, which is faster than working through this table.

| Symptom | Solution |
| --- | --- |
| **Connected, but the trackpad and keyboard do nothing** | The OS is blocking synthetic input. See [Granting Input Permission](#-granting-input-permission) — on macOS enable your **terminal app** under Accessibility and restart the server |
| Keyboard shortcuts do nothing | Same cause as above — `key_combo` goes through the same blocked path |
| Play/pause or track skip does nothing | Fixed for macOS in this version — it now posts `NSSystemDefined` events instead of pyautogui virtual keys, which macOS ignores. `stop` has no system-wide equivalent on macOS; use pause |
| Mouse moves but shortcuts don't | Accessibility is granted; check the target app isn't running elevated (Windows) or capturing the shortcut itself |
| Phone can't reach the server | Confirm both devices are on the same network, then check the firewall — this is nearly always the firewall |
| `Connection failed` in the app | Is `server.py` running? Does `http://<ip>:8765/health` load in the phone's browser? |
| Phone keeps asking to pair | The token was rejected — scan the QR again, or use a fresh pairing code from the PC |
| `Wrong or expired code` | Codes last 10 minutes and work once. Restart the server for a new one |
| Setup page says "No Server" but it's running | Safari blocks pages from reaching localhost. Use Chrome, or scan the QR printed in the terminal |
| Want to unpair every device | Restart the server and POST to `/pair/rotate` from the PC, or delete `server/config/pairing.json` |
| Server prints `127.0.0.1` | No LAN connection detected. Connect to Wi-Fi, or read the IP from `ipconfig` / `ifconfig` |
| Blank page at `:8765` | Frontend isn't built — `cd frontend && npm run build` |
| Vercel build fails | Root Directory must be set to `frontend`, not the repo root |
| Trackpad does nothing | Does the console show `Client connected`? On macOS, grant Accessibility permission |
| Stream stuck on `ESTABLISHING…` | Restart the server; if it persists: `pip install --force-reinstall aiortc av` |
| Stream is choppy | Drop to Low or Medium quality; 5 GHz Wi-Fi helps a lot |
| Volume shows `-1` | Windows: `pip install pycaw comtypes`. Linux: install `pulseaudio-utils` for `pactl` |
| Unicode typing does nothing | Linux needs a clipboard tool — `sudo apt install xclip` |
| `process_kill` → access denied | That process belongs to another user or the system; needs elevation |
| Terminal command times out | Default limit is 30s — pass `{"timeout": 120}` for long jobs |
| `ModuleNotFoundError: pycaw` on macOS/Linux | This is expected — `pycaw` is Windows-only and gated by platform markers |
| Screen recording permission on macOS | System Settings → Privacy & Security → Screen Recording → add your Terminal or Python binary |

---

## 🛠️ Development Guide

### Running in Development Mode

```bash
# Terminal 1: Frontend with hot reload on :3000
cd frontend && npm run dev

# Terminal 2: Server (restart manually after edits)
cd server && python server.py
```

Open `http://localhost:3000` on your desktop and connect to `localhost` in the connection bar. For phone testing, use your LAN IP — `next dev` binds all interfaces.

### Code Quality

```bash
npx tsc --noEmit      # TypeScript type check
npm run lint          # ESLint
npm run build         # Production static export → out/
```

### Adding a New Action

1. **Write the handler** — create or extend a controller in `server/controllers/`. Accept `**_` so unexpected payload keys don't raise:

   ```python
   class MyController:
       def my_action(self, param1: str = "", **_):
           # Your logic here
           return {"result": "success"}
   ```

2. **Register it** in the `HANDLERS` table in `server/server.py`:

   ```python
   HANDLERS = {
       ...
       "my_action": my_controller.my_action,
   }
   ```

3. **Call it from the UI** with `send("my_action", {...})` or `sendAndWait` if you need the reply.

> **Threading note:** Handlers run in a worker thread via `asyncio.to_thread()`, so blocking calls are fine. Keep anything on the input path fast, since the trackpad shares the socket.

### Adding a New Frontend Component

1. Create the component in `frontend/app/components/`
2. Import and add it to the appropriate tab in `page.tsx`
3. Use `useWebSocket()` for control messages:

   ```tsx
   const { send, sendAndWait } = useWebSocket();
   
   // Fire and forget (fast, no reply)
   send("my_action", { param1: "value" });
   
   // Wait for response (slower, gets data back)
   const result = await sendAndWait("my_action", { param1: "value" });
   ```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

- 🔐 Authentication system (shared PIN/token)
- 🎨 Theme customization UI
- 📊 System monitoring dashboard with charts
- 🔊 Per-app volume control (Windows)
- 📱 Notification forwarding
- 🖥️ Multi-monitor support for screen streaming
- 🎮 Gamepad emulation
- 📂 File upload/download support

---

## ❓ Frequently Asked Questions

<details>
<summary><b>Does SPIDER_CTRL work over the internet?</b></summary>

No, by design. Connections are gated by a pairing token, but the server is still built for a trusted LAN: traffic is plaintext by default and a paired device gets a shell on your machine. Use it on your home Wi-Fi, a personal hotspot, or an isolated LAN. For access from outside, put both devices on a [Tailscale](https://tailscale.com) network and use the Tailscale IP — that works unchanged, rather than port-forwarding this to the internet.

</details>

<details>
<summary><b>Is there any latency?</b></summary>

Over a local network, control latency is typically **under 10ms** — you won't notice it. Screen streaming latency depends on quality settings and Wi-Fi speed, typically 30–100ms on a 5 GHz network.

</details>

<details>
<summary><b>Can I use this on multiple computers?</b></summary>

Yes! Run the server on each computer. Each will broadcast its own UDP beacon. On your phone, connect to whichever IP you want to control.

</details>

<details>
<summary><b>Does it work with dual monitors?</b></summary>

The screen streaming captures the primary monitor. The mouse and keyboard control the full desktop across all monitors.

</details>

<details>
<summary><b>Can my phone and PC be on different Wi-Fi networks?</b></summary>

No — they must be on the same local network. The simplest fix is to create a hotspot on either device and connect the other to it.

</details>

<details>
<summary><b>Is my data sent to any cloud server?</b></summary>

No. All traffic stays on your local network. The only external requests are to Google STUN servers (for WebRTC NAT traversal) and Google Fonts (for the JetBrains Mono typeface). Neither carries your data.

</details>

<details>
<summary><b>Can someone on my network hack my computer through this?</b></summary>

If someone on your network can reach port 8765, they have full control — terminal, process manager, power controls, everything. Only run SPIDER_CTRL on networks you trust (home Wi-Fi, personal hotspot). See the [Security Model](#-security-model) section.

</details>

<details>
<summary><b>Why does macOS ask for permissions?</b></summary>

macOS requires explicit user consent for apps that control input (Accessibility) or capture the screen (Screen Recording). Grant these in System Settings → Privacy & Security for your terminal or Python binary.

</details>

<details>
<summary><b>Can I customize the app's appearance?</b></summary>

Yes! The theme is defined in `frontend/app/globals.css` (CSS variables) and `frontend/tailwind.config.js` (Tailwind tokens). Change both files and rebuild with `npm run build`.

</details>

---

## 📄 License

MIT — use it, fork it, change it, ship it.

---

<p align="center">
  <b>If you find SPIDER_CTRL useful, give it a ⭐ on GitHub!</b><br>
  <a href="https://github.com/muneebkhan08/test_mob_ctrl">github.com/muneebkhan08/test_mob_ctrl</a>
</p>

<!-- SEO Keywords: remote desktop control, phone remote control PC, mobile remote control computer, WebSocket remote desktop, WebRTC screen sharing, Python remote desktop, FastAPI remote control, smartphone as trackpad, phone as wireless mouse, phone as keyboard, remote PC control from phone, LAN remote desktop, local network remote control, open source remote desktop, no cloud remote desktop, privacy focused remote control, PWA remote desktop, self-hosted remote desktop, cross-platform remote control, wireless touchpad phone, mobile process manager, remote terminal from phone, screen mirroring LAN, remote volume control, remote power control, remote file browser, pyautogui remote control, Next.js PWA remote desktop -->
