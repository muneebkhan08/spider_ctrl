# Architecture

How SPIDER_CTRL is put together, and why it is put together that way.

The short version: a Python server runs on the PC and serves both an API and
the web UI. A phone on the same network opens that UI and drives the PC over a
WebSocket. A statically hosted copy of the same UI acts as an installer and
pairing screen. Nothing is relayed through a third party, and no part of the
system requires a paid service.

- [System at a glance](#system-at-a-glance)
- [Three browser rules that shaped the design](#three-browser-rules-that-shaped-the-design)
- [Why there is no cloud broker](#why-there-is-no-cloud-broker)
- [Components](#components)
- [The pairing model](#the-pairing-model)
- [Connection lifecycle](#connection-lifecycle)
- [Control channel](#control-channel)
- [Video channel](#video-channel)
- [Discovery](#discovery)
- [Deployment topology](#deployment-topology)
- [Uninstalling](#uninstalling)
- [Cost and licensing](#cost-and-licensing)
- [Known limits](#known-limits)

---

## System at a glance

```
        ┌──────────────────────────┐          ┌──────────────────────────┐
        │   Vercel (static host)   │          │        Host PC           │
        │                          │          │                          │
        │  Next.js export          │          │  FastAPI + Uvicorn :8765 │
        │   · PC connector page    │          │   · /ws      control     │
        │   · install.sh/.ps1      │          │   · /pair    pairing     │
        │   · phone remote UI      │          │   · /webrtc/* video      │
        └───────────┬──────────────┘          │   · /*       the UI      │
                    │                         │                          │
         1. open on PC, get                   │  controllers/            │
            install one-liner                 │   mouse keyboard screen  │
                    │                         │   terminal fs procs …    │
                    ▼                         └────────┬─────────────────┘
        ┌──────────────────────────┐                   │
        │  loopback probe          │  2. GET /pair     │
        │  127.0.0.1:8765/pair     │──────────────────►│
        │  → renders a QR code     │◄──────────────────┤
        └───────────┬──────────────┘   token + QR      │
                    │                                  │
         3. phone scans QR                             │
                    ▼                                  │
        ┌──────────────────────────┐   4. ws://ip:8765/ws?t=<token>
        │         Phone            │◄─────────────────►│
        │  UI served BY the PC     │   5. WebRTC video │
        └──────────────────────────┘◄─────────────────►┘
                         (all traffic stays on the LAN)
```

Two separate things are called "the app":

| | Served from | Role |
| --- | --- | --- |
| **Connector** | Vercel (or the PC itself) | Install the server, show the pairing QR |
| **Remote** | The PC, always | Actually control the machine |

They are the same Next.js build. Which one renders is decided at runtime by
viewport and pointer type — see [`page.tsx`](frontend/app/page.tsx).

---

## Three browser rules that shaped the design

Most of the non-obvious decisions here exist because a web page is not allowed
to do the obvious thing. These are hard browser rules, not bugs to engineer
around.

**1. An HTTPS page cannot scan the LAN.**
`fetch("http://192.168.1.42:8765/health")` from an HTTPS origin is blocked as
mixed content *before it reaches the network* — not even `no-cors` opaque mode
gets through. A "scan 254 addresses and find the PC" loop returns nothing,
always.

**2. JavaScript cannot read the local IP.**
The old WebRTC ICE-candidate leak was closed in Chrome 76; host candidates are
replaced with random `.local` mDNS hostnames. Firefox and Safari followed.
There is no API that hands a page `192.168.1.42`.

**3. A website cannot install software.**
One human action — download and run — is irreducible.

The single exception that makes the connector page possible: **loopback is a
"potentially trustworthy" origin.** `http://127.0.0.1` and `http://localhost`
are exempt from mixed-content blocking, so an HTTPS page *can* reach a server
on the same machine. Chrome additionally requires a Private Network Access
preflight, which the server answers — see
[`private_network_access`](server/server.py).

Safari is stricter and blocks this. That is why the server prints the same QR
code in its own terminal: two independent paths to the same information, so
neither is a single point of failure.

---

## Why there is no cloud broker

An earlier design had the PC register with a small cloud service so that a
phone could ask "which PCs share my public IP?" and discover the address
automatically. That works, and it is how commercial tools do it.

It was dropped, because the PC already knows its own IP. Having it *draw a QR
code* achieves the same result with no server, no database, no account, no
domain, and no recurring cost. The following all disappeared with it:

| Dropped | Why it is not needed |
| --- | --- |
| Redis / KV store | No registry to persist |
| Rendezvous API | The QR carries the address |
| Public-IP matching | The phone reads it off the screen |
| Domain + wildcard TLS | No hosted hostname to certify |
| TURN relay | LAN only; see [Known limits](#known-limits) |

This is the same approach Syncthing and KDE Connect take, and it is faster for
the user than discovery would have been.

---

## Components

### Frontend — `frontend/`

A Next.js 14 App Router project built with `output: "export"`, producing a
fully static bundle in `frontend/out/`. No Node runtime is needed to serve it;
the Python server hands out the files directly.

| File | Role |
| --- | --- |
| [`page.tsx`](frontend/app/page.tsx) | Picks connector vs. remote vs. pairing screen |
| [`PCConnector.tsx`](frontend/app/components/PCConnector.tsx) | Desktop setup: probe loopback, show QR or install command |
| [`PairPrompt.tsx`](frontend/app/components/PairPrompt.tsx) | Phone: six-character code entry |
| [`InputWarning.tsx`](frontend/app/components/InputWarning.tsx) | Phone: warns when the OS is blocking mouse/keyboard input |
| [`UninstallPanel.tsx`](frontend/app/components/UninstallPanel.tsx) | Desktop: danger zone for *this* install |
| [`OtherInstalls.tsx`](frontend/app/components/OtherInstalls.tsx) | Desktop: find + remove any install on the machine |
| [`useWebSocket.tsx`](frontend/app/hooks/useWebSocket.tsx) | Control channel, token storage, reconnect policy |
| [`useWebRTC.tsx`](frontend/app/hooks/useWebRTC.tsx) | Video channel, signalling, stats |
| [`ConnectionBar.tsx`](frontend/app/components/ConnectionBar.tsx) | Status, manual IP entry, unpair |

The connector/remote split is made on `(min-width: 900px) and (pointer: fine)`
rather than user agent, and returns `null` until mounted so the static export
and the first client render agree.

### Server — `server/`

FastAPI on Uvicorn, single process, port 8765.

| File | Role |
| --- | --- |
| [`server.py`](server/server.py) | App, middleware, routes, WS dispatch, UDP beacon |
| [`utils/pairing.py`](server/utils/pairing.py) | Tokens, pairing codes, origin policy, QR rendering |
| [`utils/permissions.py`](server/utils/permissions.py) | Detects whether the OS will accept synthetic input |
| [`utils/uninstall.py`](server/utils/uninstall.py) | Removal planning, cross-platform install discovery, guards |
| [`utils/network.py`](server/utils/network.py) | LAN IP detection |
| [`utils/ssl_cert.py`](server/utils/ssl_cert.py) | Self-signed certs for opt-in TLS |
| [`selftest.py`](server/selftest.py) | Health check for every subsystem, run standalone |
| `controllers/*.py` | One module per capability |

Controllers are plain classes with synchronous methods. `server.py` maps action
strings to bound methods in a single `HANDLERS` dict, and every call is run
through `asyncio.to_thread` so a slow shell command cannot stall the event loop.

Adding a capability means writing a method and adding one line to `HANDLERS`.

---

## The pairing model

### Threat model

The server exposes `terminal_execute`, `process_kill`, `power_shutdown` and
filesystem browsing. Anything that can open the WebSocket owns the machine.
Two attackers matter:

1. **Another device on the same Wi-Fi** — a café, a dorm, a shared office.
   It can reach port 8765 directly.
2. **A website the user happens to have open** — it can make their browser
   issue requests to `127.0.0.1` and, critically, **open WebSockets to it**.
   WebSocket handshakes are not subject to CORS, so a same-origin policy does
   not help here.

The second one is easy to miss and is the reason the token is mandatory even
for loopback clients.

### Defences

| Mechanism | Stops |
| --- | --- |
| **Token on every `/ws`** — 256-bit, `hmac.compare_digest` | Both attackers. No token, no connection, loopback included |
| **Origin port check** on the handshake | Hostile pages and DNS rebinding — an attacker's page is served from :80/:443, never :8765 |
| **`/pair` is loopback-only** | LAN devices simply asking for the token |
| **CORS allowlist** on `/pair` | A hostile site *reading* the token — its request does come from loopback, so the loopback check alone is not enough |
| **PNA preflight opt-in** | Adds Chrome's own gate in front of the above |
| **Code expiry + single use + attempt cap** | Brute-forcing the short code |

The token is the credential. The six-character code is only a short-lived
courier for it — that is why it expires in 10 minutes, works once, and is
destroyed after 5 wrong guesses.

### Why the WebSocket accepts before it rejects

Refusing the upgrade before `accept()` makes Starlette answer with a plain HTTP
403, which the browser reports as close code **1006** — indistinguishable from
"the server is down". The client would then retry a token that can never work,
forever.

Accepting and immediately closing with **1008** gives an unambiguous signal:
*this token is bad, stop and re-pair.* Nothing is read from the socket before
it closes, so no command can run. The client uses exactly this distinction:

```
close 1008  → clear the token, show the pairing screen
close other → keep the token, reconnect in 3s (server restarting)
```

### Token lifecycle

```
first run            server generates 256-bit token → server/config/pairing.json
                     (gitignored, chmod 600 on POSIX)
        │
        ▼
pair                 QR:   /?t=<token>         → phone stores it in localStorage
                     code: POST /pair/claim    → returns the same token
        │
        ▼
every connect        ws://host:8765/ws?t=<token>
        │
        ▼
unpair               POST /pair/rotate  (loopback only)  → new token, all devices drop
                     or delete server/config/pairing.json
```

The token is stripped from the address bar with `history.replaceState` as soon
as it is stored, so it does not linger in history, screenshots or shared links.

### Rotation reaches devices that are already connected

The token is only checked during the handshake, so rotating it would not by
itself disturb a device that is *currently* connected — which is precisely the
device you rotate to get rid of. The server therefore keeps a registry of live
sockets and revokes them on rotate.

Revocation is **signalled, not forced**: each handler races its next
`receive_text()` against a revocation flag and closes itself when the flag is
set. Closing a socket from the rotate handler while the socket's own task is
parked in `receive_text()` deadlocks, so the owning task has to do it. The
effect is immediate — connected devices drop with close code 1008 and land on
the pairing screen.

---

## Connection lifecycle

### First run, from nothing

```
PC browser                Vercel            PC server              Phone
    │                       │                   │                    │
    │─ open site ──────────►│                   │                    │
    │◄─ connector page ─────│                   │                    │
    │                       │                   │                    │
    │─ GET 127.0.0.1/pair ──────────────────────►  (nothing yet)     │
    │◄─ connection refused ─────────────────────│                    │
    │                                           │                    │
    │  shows install one-liner                  │                    │
    │                                           │                    │
    │─ user runs install.sh ───────────────────►│  installs, starts  │
    │                                           │                    │
    │─ GET 127.0.0.1/pair ─────────────────────►│                    │
    │◄─ {token, qr, code, ip} ──────────────────│                    │
    │                                           │                    │
    │  renders QR                               │                    │
    │                                           │                    │
    │                                           │◄── scan, GET /?t= ─│
    │                                           │─── UI + token ────►│
    │                                           │◄── ws?t=<token> ───│
    │                                           │─── connected ─────►│
```

### Returning phone

```
tap home-screen icon → GET http://<ip>:8765/ → token from localStorage
                     → ws?t=<token> → connected
```

No pairing, no typing. If the token is rejected (rotated, or a different PC),
the 1008 path drops it and the pairing screen appears.

---

## Control channel

WebSocket at `/ws`, JSON both ways.

**Request**

```json
{ "action": "mouse_move", "payload": { "dx": 12, "dy": -4 }, "id": "req_7" }
```

**Response** — only sent when `id` is present

```json
{ "ok": true, "data": { ... }, "id": "req_7" }
{ "ok": false, "error": "No such process", "id": "req_7" }
```

Fire-and-forget messages (mouse movement, scroll) omit `id` and get no reply,
which keeps the pointer responsive. Request/response calls use `sendAndWait`,
which resolves on the matching `id` or times out after 35 s — chosen to sit
just above the shell's own 30 s command timeout.

Handlers run in a worker thread via `asyncio.to_thread`. Without that, a single
`terminal_execute` would freeze video signalling and every other client.

---

## Video channel

WebRTC, negotiated over HTTP rather than the WebSocket so it can be established
independently of control.

```
browser: createOffer  ──► POST /webrtc/offer  ──► aiortc attaches a capture track
browser: setRemote    ◄──  {connection_id, sdp}
both:    trickle ICE  ◄─►  POST /webrtc/ice
```

Frames come from `mss`, are converted through NumPy into PyAV `VideoFrame`s,
and are encoded by aiortc. A `stats` data channel carries RTT and quality
changes without HTTP round-trips. Quality can be changed mid-stream via
`POST /webrtc/quality`.

WebRTC is used here for congestion control and loss tolerance, not for NAT
traversal — on a LAN the host candidates connect directly.

---

## Discovery

The server broadcasts a JSON beacon to UDP 8766 every 2 seconds with its
service name, version, IP, port, hostname and platform.

Note that **browsers cannot receive UDP**, so the web client does not use this.
It exists for native or scripted clients. For the web flow, the QR code is the
discovery mechanism.

---

## Deployment topology

The Vercel deployment is optional and stateless. It hosts:

- the connector page (install command + QR rendering)
- `install.sh` / `install.ps1`
- a copy of the remote UI, which redirects to the PC

It never sees a token, never proxies traffic, and can be replaced by GitHub
Pages, Cloudflare Pages, or nothing at all — the PC server serves the identical
UI at `http://<ip>:8765`.

Because the connector page reads a pairing token over loopback, the server only
answers `/pair` for origins on an explicit allowlist. Set it when your
deployment URL differs from the default:

```bash
SPIDER_CTRL_ORIGINS="https://your-app.vercel.app" python server.py
```

A wildcard here would let any site the user visits read the token and take the
machine, so the list is exact-match only.

---

## Cost and licensing

Everything in the runtime path is free and open source. There is no paid API,
no metered service, and no account to create.

| Layer | Choice | Cost | License |
| --- | --- | --- | --- |
| Site hosting | Vercel Hobby / GH Pages / CF Pages | Free | — |
| Installer hosting | GitHub Releases / static file | Free | — |
| QR (terminal + SVG) | `qrcode` | Free | BSD |
| Server | FastAPI + Uvicorn | Free | MIT / BSD |
| Video | aiortc + PyAV + mss | Free | BSD / MIT |
| Input | pyautogui | Free | BSD |
| Auth | `secrets` + `hmac`, stdlib | Free | PSF |
| TLS certs | `cryptography`, self-signed | Free | Apache/BSD |
| Off-LAN (optional) | Tailscale / Headscale | Free tier | client BSD-3 |

Deliberately avoided: managed KV stores, rendezvous services, TURN relays,
purchased domains, and code-signing certificates (~$99–200/yr), which is why
the installer is a script rather than a signed binary.

---

## Uninstalling

The uninstaller's hard problem is not deleting things, it is telling an
install apart from somebody's source checkout. Both are git repos with an
identical layout, so nothing in the tree's own shape is a safe signal.

The installers therefore write a `.spider-ctrl-install` marker, and that
marker is the only thing that authorises removing a tree whole:

| Marker | Mode | Effect |
| --- | --- | --- |
| present | `full` | The install directory is removed |
| absent | `artifacts` | Only generated paths go; source is untouched |

Layered on top:

- **Loopback only.** None of `/uninstall/plan`, `/uninstall`, `/uninstall/scan`
  or `/uninstall/remove` is reachable from a paired phone.
- **An exact confirmation phrase** in the request body, not just a flag.
- **Root sanity checks** that refuse the filesystem root, the home directory,
  well-known user folders, paths shorter than three components, and any tree
  without `server/server.py` — a backstop for a bug computing the root, and
  the same file `find_installs()` requires, so a path either function accepts
  means the same thing to both.
- **Containment re-checked at delete time**, not only when the plan is built,
  so a target that somehow escaped the root is skipped rather than removed.
- **Failures reported, not raised.** A partial uninstall the user can finish
  by hand beats an exception halfway through.

Afterwards the server revokes every live socket and stops itself, one second
later, so the response still reaches the browser — but only when the root
being deleted is its own. See below.

### Finding installs this account didn't tell it about

`plan()` and `execute()` both take an explicit `root` now, defaulting to the
running server's own tree (`install_root()`) so every existing call site keeps
working unchanged. Passing a different root routes the identical guards at a
different install entirely — which is what running install.sh twice, or
running an older version that predates the marker, leaves behind: a tree on
disk with nothing in the app pointing at it.

`find_installs()` locates those trees:

```
self (install_root())
  + Path.home() / ".spider-ctrl"      ← what both installers write to
  + $SPIDER_CTRL_HOME, if set now     ← for *this* process only, see below
  + any extra_roots the caller names  ← /uninstall/scan?path=...
      ↓ dedupe, keep only paths with server/server.py
      ↓ plan() each survivor
  sorted: self first, then by size (biggest first)
```

Both installers resolve to the identical relative path — `.spider-ctrl` under
the account's home directory — so a single `Path.home()` call finds it on
Windows, macOS and Linux with no platform branch; the OS-specific part is
already inside `Path.home()`. There is deliberately no filesystem-wide
search: scanning every directory for something that merely *looks* like
SPIDER_CTRL risks matching an unrelated project and is slow on a large disk.
A custom `SPIDER_CTRL_HOME` set once, in a different shell or a past
install, leaves no record anywhere the default scan looks — the desktop
page's *check a specific path* box exists for exactly that gap, feeding a
path straight to `/uninstall/scan?path=`.

### Is a found install currently running?

Checked with `psutil` rather than `lsof`/`netstat`, so the same code runs on
every OS. Two independent signals, either is enough:

1. Some process's command line runs a `server.py` that resolves under the
   candidate root.
2. Something is listening on 8765, and *that* process's executable or
   working directory resolves under the root.

Either check can raise `AccessDenied` on a locked-down system — SIP on
macOS, another user's process on Linux, a restricted account on Windows —
and that is treated as *unknown*, never as *not running*: a permission error
must not make a live server look safe to delete out from under. The reverse
gap — a process a permission check genuinely can't see — is why the delete
itself still surfaces OS-level file-in-use errors in `failed` rather than
trusting this signal alone.

### Deleting a tree that isn't the one running

`execute()` returns `self` (was the deleted root this process's own tree?)
alongside `shutdown`, and `shutdown` is only ever true when `self` is. Without
that distinction, a request to clean up a leftover install elsewhere on disk
would kill the server answering the request — which is also the server the
response has to travel back through. `/uninstall/remove` is the endpoint this
matters for: it deletes whatever `root` the caller names, and the caller is
very often *not* deleting the tree currently serving the request.

`/uninstall/remove` does not keep its own allowlist of "known" roots to check
the request against — an earlier version did, and it was a real bug: since
`/uninstall/scan?path=` can surface a root outside the server's own default
scan locations, cross-checking against that default scan rejected every
custom path the scan itself had just found. `plan()`/`execute()` already
apply the complete sanity check to whatever root is passed, so the endpoint
just calls them directly; that check *is* the allowlist.

## Known limits

**Same network only.** There is no relay. For off-LAN access, install Tailscale
on both devices and enter the Tailscale IP — it works unchanged and costs
nothing. A built-in relay would need a TURN server, which is the one component
that cannot be free at scale.

**HTTP on the LAN.** The phone talks to the PC over plain HTTP unless
`SPIDER_CTRL_TLS=1` is set, and that uses a self-signed certificate, so the
browser warns. A trusted certificate would need a purchased domain and per-install
issuance. Consequence: no service worker and no full PWA install from the LAN
origin, since those require a secure context. iOS "Add to Home Screen" still
works.

**The token is device-scoped, not user-scoped.** Anyone holding the phone holds
the pairing. Revocation is all-or-nothing: `/pair/rotate` immediately drops
every connected device and invalidates every stored token, so the other devices
have to pair again too.

**No confirmation prompt on the PC.** Pairing is the only gate; once paired, a
device can shut the machine down without further approval. An approval dialog on
the host is the obvious next hardening step.

**Media keys are not keyboard keys on macOS.** pyautogui maps `playpause`,
`nexttrack` and `prevtrack` to `None` there, so pressing them posted nothing
and reported success. The controller now posts `NSSystemDefined` events
directly on macOS and keeps pyautogui elsewhere. macOS has no system-wide
stop key, so `stop` reports that rather than claiming to have worked.

**Input needs an OS permission that fails silently.** pyautogui does not raise
when macOS or Wayland refuses synthetic events — it returns normally and
nothing happens, so every control appears to work while doing nothing. The
server checks `AXIsProcessTrusted` at boot and exposes an `input_status`
action, and the UI shows a banner, but the permission itself can only be
granted by hand. On macOS it belongs to the *responsible* process — the
terminal app the server was launched from, not the Python binary — which is
the part that most often trips people up.

There is deliberately no in-app permission prompt: building the CFDictionary
that `AXIsProcessTrustedWithOptions` needs through ctypes segfaulted the
interpreter, and that call would have sat in the startup path.

**DHCP can move the address.** The stored IP may go stale after a router
restart; the app falls back to the pairing screen and the QR fixes it. Reserving
a static lease avoids it entirely.
