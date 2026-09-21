# Deployment Guide — SPIDER_CTRL Remote

Complete step-by-step guide to deploy the frontend on **Vercel** and run the backend server on your PC.

---

## Part 1: Deploy Frontend to Vercel

### Prerequisites

- A [GitHub](https://github.com) account
- A [Vercel](https://vercel.com) account (free tier works)
- Repository pushed to GitHub (already done → `muneebkhan08/test_mob_ctrl`)

---

### Step 1 — Import Project in Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **"Add New…"** → **"Project"**
3. Under **"Import Git Repository"**, find and select **`muneebkhan08/test_mob_ctrl`**
4. Click **"Import"**

---

### Step 2 — Configure Project Settings

On the **"Configure Project"** page, set the following:

| Setting | Value |
| --- | --- |
| **Project Name** | `spider-ctrl` (or any name you prefer) |
| **Framework Preset** | **Next.js** |
| **Root Directory** | `frontend` ← ⚠️ **Critical — click "Edit" and type `frontend`** |
| **Build Command** | `next build` (auto-detected, leave default) |
| **Output Directory** | `.next` (auto-detected, leave default) |
| **Install Command** | `npm install` (auto-detected, leave default) |
| **Node.js Version** | `20.x` (default is fine) |

#### How to set Root Directory

1. In the **"Configure Project"** screen, find **"Root Directory"**
2. Click the **"Edit"** button next to it
3. Type **`frontend`** in the text field
4. You should see it detect `package.json` inside `frontend/`
5. Confirm the selection

> **Why?** The repo has both `frontend/` and `server/` folders. Vercel only needs to build the Next.js app inside `frontend/`.

---

### Step 3 — Environment Variables (Optional)

None are required for Vercel.

On the **PC server** side, two variables are worth knowing:

| Key | Purpose | Default |
| --- | --- | --- |
| `SPIDER_CTRL_ORIGINS` | Comma-separated list of hosted sites allowed to read `/pair`. Set this if your Vercel URL isn't the default. | `https://spider-ctrl.vercel.app` |
| `SPIDER_CTRL_NO_BROWSER` | Set to `1` to stop the server opening the setup page on boot (headless installs). | unset |

> ⚠️ `SPIDER_CTRL_ORIGINS` must list exact origins. The `/pair` response carries
> the pairing token, so a wildcard here would let any site that the user visits
> read it and take over the machine.

---

### Step 4 — Deploy

1. Click **"Deploy"**
2. Wait for the build to complete (usually 30–60 seconds)
3. You'll see a success screen with your deployment URL

Your app is now live at:

```text
https://spider-ctrl.vercel.app
```

(or whatever project name you chose)

---

### Step 5 — Verify Deployment

1. Open the Vercel URL on your phone's browser
2. You should see the SPIDER_CTRL app with:
   - The connection bar at the top
   - Bottom tab navigation (Pad / Keys / Tools / Control)
3. The app will show "Disconnected" — that's expected until you start the server

---

## Part 2: Set Up the PC Server

The Python server runs **locally on your PC** — it is NOT deployed to Vercel.

### Step 1 — Install Python Dependencies

```bash
cd server

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate           # Windows (Command Prompt)
# or
.\venv\Scripts\Activate.ps1     # Windows (PowerShell)
# or
source venv/bin/activate        # Mac/Linux

# Install packages
pip install -r requirements.txt
```

### Step 2 — Start the Server

```bash
python server.py
```

Or simply double-click **`start-server.bat`** from the project root
(macOS/Linux: run `./start-server.sh`).

You'll see:

```text
════════════════════════════════════════════════════════
  🖥️  SPIDER_CTRL Server v1.0.0
  🌐  Open on phone → http://192.168.1.42:8765
  🔌  WebSocket  →  ws://192.168.1.42:8765/ws
  🎥  WebRTC     →  /webrtc/offer
  📡  UDP Disco   →  port 8766
  💻  Platform    →  Windows 10
════════════════════════════════════════════════════════
```

**Note the IP address** — you'll need it on your phone.

### Step 3 — Allow Through Firewall (if needed)

If your phone can't connect, Windows Firewall may be blocking the server:

1. Open **Windows Defender Firewall**
2. Click **"Allow an app or feature through Windows Defender Firewall"**
3. Click **"Change settings"** → **"Allow another app…"**
4. Browse to `server\venv\Scripts\python.exe`
5. Check **Private** only — never Public
6. Click **OK**

Alternatively, run in an elevated PowerShell:

```powershell
New-NetFirewallRule -DisplayName "SPIDER_CTRL Server" -Direction Inbound -Protocol TCP -LocalPort 8765 -Profile Private -Action Allow
New-NetFirewallRule -DisplayName "SPIDER_CTRL Discovery" -Direction Inbound -Protocol UDP -LocalPort 8766 -Profile Private -Action Allow
```

---

## Part 3: Connect Phone to PC

Every device pairs once. Pairing hands the phone a token it stores and reuses,
so this only happens the first time.

### Fastest: open the site on the PC

1. Open `https://spider-ctrl.vercel.app` **on the PC itself**
2. It detects the running server and shows a **QR code** — if the server isn't
   installed yet, it shows the one-line install command instead
3. Scan the QR with your phone's camera and open the link
4. Done — the QR carries the token, so the phone pairs and connects itself ✅

> The page finds the server by asking `http://127.0.0.1:8765/pair`. Chrome,
> Edge and Firefox allow this; Safari blocks it, so in Safari use the QR code
> the server prints in its terminal instead.

### No camera: pairing code

1. Open the address the server printed (e.g. `http://192.168.1.42:8765`)
2. Enter the six-character code shown on the PC
3. Status turns green → you're in! ✅

The code works once and expires after ten minutes. Restart the server for a
fresh one.

### From the deployed site on the phone

1. Open `https://spider-ctrl.vercel.app` on your phone
2. Expand the connection bar, enter the PC's IP, tap **Go**
3. You land on the PC-served app — pair with the code as above

> The deployed site can't drive the PC directly: an HTTPS page is not allowed
> to open a plain `ws://` connection to your LAN. It hands off to the server
> instead, which is why the QR route is smoother.

### Using PC as Hotspot

1. **PC:** Settings → Network → Mobile Hotspot → Turn On
2. **Phone:** Connect to the PC's hotspot
3. **PC IP is usually:** `192.168.137.1`
4. Enter that IP in the app and connect

### Using Phone as Hotspot

1. **Phone:** Enable hotspot
2. **PC:** Connect to the phone's hotspot
3. Start the server → note the IP shown in console
4. Enter that IP in the app

---

## Part 4: Add to Home Screen (PWA)

For a native app-like experience on your phone:

### iOS (Safari)

1. Open the Vercel URL in Safari
2. Tap the **Share** button (square with arrow)
3. Scroll down → tap **"Add to Home Screen"**
4. Tap **"Add"**

### Android (Chrome)

1. Open the Vercel URL in Chrome
2. Tap the **⋮** menu (three dots)
3. Tap **"Add to Home screen"** or **"Install app"**
4. Tap **"Add"**

The app will now appear as an icon on your home screen and open in full-screen mode.

---

## Vercel Settings Summary

Quick reference for all Vercel configuration:

```text
Project Name:       spider-ctrl
Framework Preset:   Next.js
Root Directory:     frontend
Build Command:      next build         (default)
Output Directory:   .next              (default)
Install Command:    npm install        (default)
Node.js Version:    20.x               (default)
Env Variables:      none required
```

---

## Troubleshooting

| Problem | Solution |
| --- | --- |
| Vercel build fails | Ensure **Root Directory** is set to `frontend` |
| Setup page says "No Server" but it is running | Safari blocks page→localhost requests. Use Chrome, or scan the QR from the server's terminal |
| Phone keeps returning to the pairing screen | The token was rejected. Scan the QR again or use a fresh code |
| `Wrong or expired code` | Codes last 10 minutes and work once — restart the server for a new one |
| Unpair every device | Delete `server/config/pairing.json` and restart, or POST `/pair/rotate` from the PC |
| "Connection failed" on phone | Check both devices are on the same network |
| Firewall blocking | Allow `python.exe` through Windows Firewall (see Step 3 above) |
| Can't find PC IP | Look at the server console output when you start `server.py` |
| Touchpad not moving | Ensure the server console shows "Client connected" |
| App shows blank page | Clear browser cache and reload |
| WebSocket timeout | Try using the PC's hotspot instead of router Wi-Fi |

---

## Redeployment

Vercel auto-deploys on every push to `main`:

```bash
git add .
git commit -m "update"
git push
```

Vercel will automatically rebuild and deploy within ~60 seconds.

To manually trigger a redeploy:

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to **Deployments** tab
4. Click **⋮** on the latest deployment → **"Redeploy"**
