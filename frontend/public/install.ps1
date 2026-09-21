# SPIDER_CTRL installer for Windows.
#
#   irm https://spider-ctrl.vercel.app/install.ps1 | iex
#
# Clones (or updates) the repo, builds the UI, installs the Python deps into a
# virtualenv, and starts the server. Re-running it is safe.

$ErrorActionPreference = 'Stop'

$Repo = if ($env:SPIDER_CTRL_REPO) { $env:SPIDER_CTRL_REPO } else { 'https://github.com/muneebkhan08/test_mob_ctrl.git' }
$Dest = if ($env:SPIDER_CTRL_HOME) { $env:SPIDER_CTRL_HOME } else { Join-Path $HOME '.spider-ctrl' }
$Port = 8765

function Say  ($m) { Write-Host "[*] $m" -ForegroundColor Cyan }
function Warn ($m) { Write-Host "[!] $m" -ForegroundColor Yellow }
function Die  ($m) { Write-Host "[x] $m" -ForegroundColor Red; exit 1 }
function Have ($c) { $null -ne (Get-Command $c -ErrorAction SilentlyContinue) }

Write-Host ''
Write-Host '  SPIDER_CTRL - installer' -ForegroundColor Cyan
Write-Host ''

# ── Prerequisites ───────────────────────────────────────────────────────────
if (-not (Have 'git')) { Die 'Git is required. Install it from https://git-scm.com and re-run.' }

$Py = if (Have 'python') { 'python' } elseif (Have 'py') { 'py' } else { $null }
if (-not $Py) { Die 'Python 3.9+ is required. Install it from https://python.org (tick "Add to PATH") and re-run.' }

& $Py -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'
if ($LASTEXITCODE -ne 0) { Die 'Python 3.9+ is required.' }

if (-not (Have 'npm')) { Die 'Node.js 18+ is required. Install it from https://nodejs.org and re-run.' }

# ── Fetch ───────────────────────────────────────────────────────────────────
if (Test-Path (Join-Path $Dest '.git')) {
  Say "Updating existing install at $Dest"
  git -C $Dest pull --ff-only --quiet
  if ($LASTEXITCODE -ne 0) { Warn 'Could not fast-forward; using the local copy.' }
} else {
  Say "Cloning into $Dest"
  git clone --depth 1 --quiet $Repo $Dest
}

# ── Frontend ────────────────────────────────────────────────────────────────
if (-not (Test-Path (Join-Path $Dest 'frontend\out\index.html'))) {
  Say 'Building the UI (first run only, ~1 min)'
  Push-Location (Join-Path $Dest 'frontend')
  npm install --silent
  npm run build | Out-Null
  Pop-Location
}

# ── Python env ──────────────────────────────────────────────────────────────
$Venv   = Join-Path $Dest 'server\venv'
$VenvPy = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path $VenvPy)) {
  Say 'Creating the Python environment'
  & $Py -m venv $Venv
}
Say 'Installing Python dependencies'
& $VenvPy -m pip install --quiet --upgrade pip
& $VenvPy -m pip install --quiet -r (Join-Path $Dest 'server\requirements.txt')

# ── Firewall ────────────────────────────────────────────────────────────────
# Private profile only: this should never be reachable from a public network.
$admin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
         ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($admin) {
  if (-not (Get-NetFirewallRule -DisplayName 'SPIDER_CTRL Server' -ErrorAction SilentlyContinue)) {
    Say "Opening port $Port on private networks"
    New-NetFirewallRule -DisplayName 'SPIDER_CTRL Server' -Direction Inbound `
      -Protocol TCP -LocalPort $Port -Profile Private -Action Allow | Out-Null
  }
} else {
  Warn "Not running as admin - skipped the firewall rule."
  Warn "If your phone can't connect, run this in an admin PowerShell:"
  Warn "  New-NetFirewallRule -DisplayName 'SPIDER_CTRL Server' -Direction Inbound -Protocol TCP -LocalPort $Port -Profile Private -Action Allow"
}

# ── Launch ──────────────────────────────────────────────────────────────────
Write-Host ''
Say 'Starting the server - scan the QR code below with your phone.'
Write-Host ''
Set-Location (Join-Path $Dest 'server')
& $VenvPy server.py
