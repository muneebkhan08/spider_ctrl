"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import {
  Loader2,
  Monitor,
  Copy,
  Check,
  Terminal as TerminalIcon,
  Smartphone,
  ShieldCheck,
  RefreshCw,
  Download,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const SERVER_PORT = 8765;
const POLL_INTERVAL = 2500;

/** The site this page was served from, used to build the install one-liners. */
function siteOrigin(): string {
  if (typeof window === "undefined") return "";
  // When the PC server is serving us there is no public site to curl from,
  // so fall back to the canonical deployment.
  return window.location.port === String(SERVER_PORT)
    ? "https://spider-ctrl.vercel.app"
    : window.location.origin;
}

/**
 * Where to look for a local server.
 *
 * From the deployed site this is a cross-origin request to a private address,
 * which browsers normally forbid — loopback is the documented exception, and
 * the server answers Chrome's Private Network Access preflight to opt in.
 */
function pairEndpoint(): string {
  if (typeof window === "undefined") return "";
  return window.location.port === String(SERVER_PORT)
    ? "/pair"
    : `http://127.0.0.1:${SERVER_PORT}/pair`;
}

interface PairInfo {
  hostname: string;
  ip: string;
  port: number;
  platform: string;
  url: string;
  code: string;
  qr: string | null;
}

type OS = "windows" | "mac" | "linux";

function detectOS(): OS {
  if (typeof navigator === "undefined") return "windows";
  const ua = navigator.userAgent.toLowerCase();
  if (ua.includes("win")) return "windows";
  if (ua.includes("mac")) return "mac";
  return "linux";
}

const OS_LABEL: Record<OS, string> = {
  windows: "WINDOWS",
  mac: "MACOS",
  linux: "LINUX",
};

function installCommand(os: OS, origin: string): string {
  return os === "windows"
    ? `irm ${origin}/install.ps1 | iex`
    : `curl -fsSL ${origin}/install.sh | sh`;
}

// ── Copy-to-clipboard button ────────────────────────────────────────────────
function CopyButton({ text, label }: { text: string; label?: string }) {
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => () => clearTimeout(timer.current), []);

  const copy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Clipboard API needs a secure context; fall back to a hidden textarea.
      try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      } catch {
        return;
      }
    }
    setCopied(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setCopied(false), 1600);
  }, [text]);

  return (
    <button
      onClick={copy}
      className="shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 rounded text-[10px] font-bold tracking-[0.1em] uppercase bg-accent/10 text-accent border border-accent/25 hover:bg-accent/20 active:scale-95 transition-all"
      aria-label={copied ? "Copied" : `Copy ${label ?? "to clipboard"}`}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

// ── Main ────────────────────────────────────────────────────────────────────
export default function PCConnector({ onUseAsRemote }: { onUseAsRemote?: () => void }) {
  const [info, setInfo] = useState<PairInfo | null>(null);
  const [probing, setProbing] = useState(true);
  const [os, setOs] = useState<OS>("windows");
  const [origin, setOrigin] = useState("");
  const [blocked, setBlocked] = useState(false);

  useEffect(() => {
    setOs(detectOS());
    setOrigin(siteOrigin());
  }, []);

  // Poll for a local server until one answers, then keep the QR fresh.
  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    let attempts = 0;

    const probe = async () => {
      try {
        const res = await fetch(pairEndpoint(), { cache: "no-store" });
        if (!res.ok) throw new Error(String(res.status));
        const data: PairInfo = await res.json();
        if (cancelled) return;
        setInfo(data);
        setBlocked(false);
      } catch {
        if (cancelled) return;
        setInfo(null);
        attempts += 1;
        // A handful of instant failures with no server ever seen usually means
        // the browser refused the loopback request rather than that nothing is
        // listening — Safari does this. Surface the terminal fallback.
        if (attempts >= 3) setBlocked(true);
      } finally {
        if (!cancelled) {
          setProbing(false);
          timer = setTimeout(probe, POLL_INTERVAL);
        }
      }
    };

    probe();
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, []);

  const cmd = installCommand(os, origin);

  return (
    <div className="min-h-[100dvh] w-full overflow-y-auto hex-pattern">
      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* ── Header ─────────────────────────── */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded border border-accent/30 bg-accent/5 flex items-center justify-center shadow-glow-sm">
              <ShieldCheck size={17} className="text-accent" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-[0.2em] uppercase text-accent text-glow">
                SPIDER_CTRL
              </h1>
              <p className="text-[9px] tracking-[0.15em] text-surface-500 uppercase">
                pc connector
              </p>
            </div>
          </div>

          <div
            className={`flex items-center gap-2 rounded px-3 py-1.5 border text-[10px] font-semibold tracking-[0.12em] uppercase ${
              info
                ? "bg-accent/5 border-accent/20 text-accent"
                : "bg-surface-800/60 border-surface-700/40 text-surface-500"
            }`}
          >
            <div
              className={`w-1.5 h-1.5 rounded-full ${
                info ? "bg-accent status-connected" : "bg-surface-500"
              }`}
            />
            {probing ? "Scanning" : info ? "Server Online" : "No Server"}
          </div>
        </header>

        <AnimatePresence mode="wait">
          {probing && !info ? (
            /* ── First probe still in flight ───────────────── */
            /* Without this the install card flashes for a moment on every
               load, telling people with a running server to install it. */
            <motion.div
              key="probing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="glass rounded-xl px-5 py-6 flex items-center gap-3"
            >
              <Loader2 size={16} className="text-accent animate-spin shrink-0" />
              <div>
                <p className="text-[11px] text-surface-300">
                  Looking for a server on this PC…
                </p>
                <p className="text-[9px] text-surface-600 font-mono">
                  127.0.0.1:{SERVER_PORT}/pair
                </p>
              </div>
            </motion.div>
          ) : info ? (
            /* ── Online: show the QR ───────────────────────── */
            <motion.div
              key="online"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
              className="grid md:grid-cols-[auto_1fr] gap-6 items-start"
            >
              {/* QR panel */}
              <div className="glass rounded-xl p-6 border-glow flex flex-col items-center gap-4">
                {/* QR modules are dark, so they need a light plate to scan
                    against — this is the one deliberately bright surface. */}
                <div className="bg-white rounded-lg p-3 shadow-glow">
                  {info.qr ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={info.qr}
                      alt={`Pairing QR code for ${info.hostname}`}
                      width={208}
                      height={208}
                      className="w-52 h-52 block"
                    />
                  ) : (
                    <div className="w-52 h-52 flex items-center justify-center text-[10px] text-center text-surface-800 px-4 font-mono">
                      QR unavailable — install the
                      <br />
                      qrcode package, or use the code
                    </div>
                  )}
                </div>
                <p className="text-[10px] tracking-[0.15em] uppercase text-surface-500 text-center">
                  // scan with phone camera
                </p>
              </div>

              {/* Details panel */}
              <div className="space-y-4">
                <div className="glass rounded-xl p-5 space-y-4">
                  <div className="flex items-center gap-2 text-accent">
                    <Smartphone size={14} />
                    <h2 className="text-[11px] font-bold tracking-[0.15em] uppercase text-glow">
                      Pair your phone
                    </h2>
                  </div>

                  <ol className="space-y-2.5 text-[11px] text-surface-300 leading-relaxed">
                    <li className="flex gap-2.5">
                      <span className="text-accent font-bold shrink-0">01</span>
                      Connect the phone to the same Wi-Fi as this PC.
                    </li>
                    <li className="flex gap-2.5">
                      <span className="text-accent font-bold shrink-0">02</span>
                      Point the camera at the QR code and open the link.
                    </li>
                    <li className="flex gap-2.5">
                      <span className="text-accent font-bold shrink-0">03</span>
                      That&apos;s it — the phone pairs and connects itself.
                    </li>
                  </ol>
                </div>

                {/* Manual fallback */}
                <div className="glass rounded-xl p-5 space-y-3">
                  <p className="text-[9px] font-bold tracking-[0.15em] uppercase text-surface-500">
                    // no camera? type this instead
                  </p>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-surface-900/90 border border-surface-700/40 rounded-lg px-3 py-2.5">
                      <p className="text-[8px] tracking-[0.15em] uppercase text-surface-600 mb-1">
                        Address
                      </p>
                      <p className="text-xs font-mono text-accent break-all">
                        {info.ip}:{info.port}
                      </p>
                    </div>
                    <div className="bg-surface-900/90 border border-surface-700/40 rounded-lg px-3 py-2.5">
                      <p className="text-[8px] tracking-[0.15em] uppercase text-surface-600 mb-1">
                        Pairing code
                      </p>
                      <p className="text-xs font-mono text-accent tracking-[0.2em]">
                        {info.code}
                      </p>
                    </div>
                  </div>
                  <p className="text-[9px] text-surface-600 leading-relaxed">
                    Code expires in 10 minutes and works once. Restart the server
                    for a fresh one.
                  </p>
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-surface-600 px-1">
                  <span>
                    <span className="text-surface-500">host:</span>{" "}
                    <span className="text-surface-300">{info.hostname}</span>
                    <span className="text-surface-700"> · </span>
                    <span className="text-surface-300">{info.platform}</span>
                  </span>
                  {onUseAsRemote && (
                    <button
                      onClick={onUseAsRemote}
                      className="text-surface-500 hover:text-accent transition-colors tracking-[0.1em] uppercase text-[9px]"
                    >
                      Use this browser as remote →
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          ) : (
            /* ── Offline: install instructions ─────────────── */
            <motion.div
              key="offline"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25 }}
              className="space-y-5"
            >
              <div className="glass rounded-xl p-6 scan-line">
                <div className="flex items-center gap-2 text-accent mb-2">
                  <Download size={15} />
                  <h2 className="text-xs font-bold tracking-[0.15em] uppercase text-glow">
                    Install the server on this PC
                  </h2>
                </div>
                <p className="text-[11px] text-surface-400 leading-relaxed mb-5 max-w-2xl">
                  Your phone talks to a small server running here. Paste one line
                  into a terminal — it installs, opens the firewall port, and
                  starts automatically. This page picks it up the moment it&apos;s live.
                </p>

                {/* OS picker */}
                <div className="flex gap-0.5 p-0.5 rounded-lg bg-surface-900/90 border border-surface-700/30 w-fit mb-3">
                  {(["windows", "mac", "linux"] as OS[]).map((o) => (
                    <button
                      key={o}
                      onClick={() => setOs(o)}
                      className={`px-4 py-1.5 rounded text-[10px] font-medium tracking-[0.12em] transition-all ${
                        os === o
                          ? "bg-accent/10 text-accent border border-accent/20 text-glow"
                          : "text-surface-500 border border-transparent hover:text-surface-300"
                      }`}
                    >
                      {OS_LABEL[o]}
                    </button>
                  ))}
                </div>

                {/* Command */}
                <div className="flex items-center gap-2 bg-surface-950/80 border border-surface-700/40 rounded-lg px-3 py-2.5">
                  <TerminalIcon size={13} className="text-surface-600 shrink-0" />
                  <code className="flex-1 text-[11px] font-mono text-surface-200 overflow-x-auto whitespace-nowrap select-text">
                    {cmd}
                  </code>
                  <CopyButton text={cmd} label="install command" />
                </div>

                <p className="text-[9px] text-surface-600 mt-2.5 leading-relaxed">
                  {os === "windows"
                    ? "// run in PowerShell — needs Python 3.9+ and Node 18+"
                    : "// run in Terminal — needs Python 3.9+ and Node 18+"}
                </p>
              </div>

              {/* Waiting state */}
              <div className="glass rounded-xl px-5 py-4 flex items-center gap-3">
                <Loader2 size={15} className="text-accent animate-spin shrink-0" />
                <div className="min-w-0">
                  <p className="text-[11px] text-surface-300">
                    Watching for a server on this machine…
                  </p>
                  <p className="text-[9px] text-surface-600 font-mono truncate">
                    127.0.0.1:{SERVER_PORT}/pair · retrying every 2.5s
                  </p>
                </div>
              </div>

              {blocked && (
                <div className="rounded-xl px-5 py-4 bg-warning/5 border border-warning/20 space-y-1.5">
                  <p className="text-[10px] font-bold tracking-[0.12em] uppercase text-warning">
                    // already started the server?
                  </p>
                  <p className="text-[11px] text-surface-400 leading-relaxed">
                    Some browsers (Safari in particular) block pages from reaching
                    localhost, so this page can&apos;t see it. The server prints the
                    same QR code in its terminal window — scan it from there, or
                    open{" "}
                    <code className="bg-surface-800 px-1.5 py-0.5 rounded text-accent/80 border border-surface-700/30">
                      http://localhost:{SERVER_PORT}
                    </code>{" "}
                    in Chrome.
                  </p>
                </div>
              )}

              <div className="flex items-center gap-2 text-[9px] text-surface-600 px-1">
                <RefreshCw size={10} />
                <span>
                  Already installed? Start it with{" "}
                  <code className="bg-surface-800/60 px-1.5 py-0.5 rounded text-surface-400">
                    {os === "windows" ? "start-server.bat" : "./start-server.sh"}
                  </code>
                </span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Footer note ───────────────────── */}
        <p className="mt-10 text-[9px] text-surface-700 leading-relaxed max-w-2xl">
          <Monitor size={9} className="inline mr-1 -mt-0.5" />
          Everything stays on your network — the server runs on this PC and your
          phone talks to it directly. Nothing is relayed through a third party.
        </p>
      </div>
    </div>
  );
}
