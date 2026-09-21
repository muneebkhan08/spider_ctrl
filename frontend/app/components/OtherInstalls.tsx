"use client";

import { useState, useCallback, useEffect } from "react";
import {
  Search,
  Trash2,
  Loader2,
  Check,
  ChevronDown,
  ChevronUp,
  FolderSearch,
  HardDrive,
  CircleDot,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const SERVER_PORT = 8765;

function apiBase(): string {
  if (typeof window === "undefined") return "";
  return window.location.port === String(SERVER_PORT)
    ? ""
    : `http://127.0.0.1:${SERVER_PORT}`;
}

interface Install {
  mode: "full" | "artifacts";
  managed: boolean;
  root: string;
  items: { path: string; label: string; bytes: number }[];
  total_bytes: number;
  confirm_phrase: string;
  blocked: string | null;
  running: boolean;
  notes: string[];
  is_self: boolean;
}

function mb(bytes: number): string {
  if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
  if (bytes >= 1e6) return `${Math.round(bytes / 1e6)} MB`;
  if (bytes >= 1e3) return `${Math.round(bytes / 1e3)} KB`;
  return `${bytes} B`;
}

/** The default install path install.sh / install.ps1 use, per OS family. */
function defaultPathHint(platform: string): string {
  return platform === "Windows"
    ? "%USERPROFILE%\\.spider-ctrl"
    : "~/.spider-ctrl";
}

// ── One found install, with its own confirm-to-delete flow ─────────────────
function InstallRow({
  install,
  onRemoved,
}: {
  install: Install;
  onRemoved: (root: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [removed, setRemoved] = useState(false);

  const run = useCallback(async () => {
    if (confirm !== install.confirm_phrase) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/uninstall/remove`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ root: install.root, confirm }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        setError(data.error ?? `Failed (${res.status}).`);
      } else {
        setRemoved(true);
        onRemoved(install.root);
      }
    } catch {
      setError("Could not reach the server.");
    } finally {
      setBusy(false);
    }
  }, [confirm, install, onRemoved]);

  if (removed) {
    return (
      <div className="flex items-center gap-2 px-3 py-2.5 text-accent">
        <Check size={12} />
        <span className="text-[10px] font-mono truncate">{install.root} — removed</span>
      </div>
    );
  }

  return (
    <div className="border-b border-surface-800/60 last:border-b-0">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between gap-3 px-3 py-2.5 text-left hover:bg-surface-800/30 transition-colors"
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <code className="text-[10px] font-mono text-surface-300 truncate">
              {install.root}
            </code>
            {install.running && (
              <span className="shrink-0 flex items-center gap-1 text-[8px] font-bold tracking-wider uppercase text-accent bg-accent/10 border border-accent/25 rounded px-1.5 py-0.5">
                <CircleDot size={8} /> running
              </span>
            )}
          </div>
          <p className="text-[9px] text-surface-600 mt-0.5">
            {install.mode === "full" ? "full install" : "working copy — source kept"} ·{" "}
            {mb(install.total_bytes)}
          </p>
        </div>
        {expanded ? <ChevronUp size={12} className="shrink-0 text-surface-500" /> : <ChevronDown size={12} className="shrink-0 text-surface-500" />}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-2.5">
              {install.blocked ? (
                <p className="text-[10px] font-mono text-warning">Refused: {install.blocked}</p>
              ) : (
                <>
                  {install.items.length > 0 && (
                    <div className="rounded-lg bg-surface-950/70 border border-surface-700/40 divide-y divide-surface-800/60">
                      {install.items.map((i) => (
                        <div key={i.path} className="flex items-center justify-between px-2.5 py-1.5 gap-3">
                          <code className="text-[9px] font-mono text-surface-400 truncate">{i.label}</code>
                          <span className="text-[8px] font-mono text-surface-600 shrink-0">{mb(i.bytes)}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {install.notes.map((n) => (
                    <p key={n} className="text-[9px] text-surface-500 leading-relaxed">· {n}</p>
                  ))}
                  {install.items.length === 0 ? (
                    <p className="text-[9px] text-surface-600">Nothing to remove here.</p>
                  ) : (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={confirm}
                        onChange={(e) => setConfirm(e.target.value)}
                        placeholder={install.confirm_phrase}
                        aria-label={`Type ${install.confirm_phrase} to confirm removing ${install.root}`}
                        autoComplete="off"
                        className="flex-1 px-2.5 py-1.5 rounded text-[10px] font-mono bg-surface-950/80 border border-surface-700/40 placeholder:text-surface-700 focus:outline-none focus:border-danger/40 text-danger select-text"
                      />
                      <button
                        onClick={run}
                        disabled={confirm !== install.confirm_phrase || busy}
                        className="px-3 py-1.5 rounded text-[9px] font-bold tracking-[0.1em] uppercase bg-danger/15 text-danger border border-danger/30 disabled:opacity-25 disabled:cursor-not-allowed hover:bg-danger/25 active:scale-95 transition-all flex items-center gap-1.5 shrink-0"
                      >
                        {busy ? <Loader2 size={11} className="animate-spin" /> : <Trash2 size={11} />}
                        {busy ? "…" : "Delete"}
                      </button>
                    </div>
                  )}
                  {error && (
                    <p className="text-[9px] font-mono text-danger">{error}</p>
                  )}
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Full section: scan + list + custom-path check ───────────────────────────
/**
 * Finds every SPIDER_CTRL install this account can see — not just the one
 * currently running — and lets each be removed independently.
 *
 * Exists because install.sh / install.ps1 write to the same default
 * location every time (~/.spider-ctrl, or %USERPROFILE%\.spider-ctrl on
 * Windows — same relative path, resolved through the OS's home directory),
 * so running the installer more than once, or having run an older version
 * that predates the safety marker, leaves orphaned copies with nothing in
 * this app pointing at them. Works identically on Windows, macOS and Linux:
 * the backend does the platform-specific work, this just renders paths.
 */
export default function OtherInstalls({ platform }: { platform: string }) {
  const [open, setOpen] = useState(false);
  const [installs, setInstalls] = useState<Install[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customPath, setCustomPath] = useState("");
  const [checking, setChecking] = useState(false);

  const scan = useCallback(async (extra?: string) => {
    setLoading(true);
    setError(null);
    try {
      const qs = extra ? `?path=${encodeURIComponent(extra)}` : "";
      const res = await fetch(`${apiBase()}/uninstall/scan${qs}`, { cache: "no-store" });
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      setInstalls(data.installs.filter((i: Install) => !i.is_self));
    } catch {
      setError("Could not reach the server on this machine.");
    } finally {
      setLoading(false);
      setChecking(false);
    }
  }, []);

  useEffect(() => {
    if (open && installs === null) scan();
  }, [open, installs, scan]);

  const checkCustomPath = useCallback(() => {
    const path = customPath.trim();
    if (!path) return;
    setChecking(true);
    scan(path);
  }, [customPath, scan]);

  const handleRemoved = useCallback((root: string) => {
    setInstalls((prev) => prev?.filter((i) => i.root !== root) ?? prev);
  }, []);

  return (
    <div className="mt-3">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-[9px] font-mono tracking-[0.1em] uppercase text-surface-600 hover:text-warning transition-colors"
      >
        <FolderSearch size={10} />
        // find other installs on this machine
        {open ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-3 rounded-xl border border-surface-700/40 bg-surface-900/60 p-4 space-y-3">
              <div className="flex items-center gap-2 text-surface-400">
                <HardDrive size={12} />
                <p className="text-[9px] tracking-[0.15em] uppercase">
                  Scans the default location on {platform || "this OS"}:{" "}
                  <code className="text-surface-300">{defaultPathHint(platform)}</code>
                </p>
              </div>

              {loading && (
                <p className="flex items-center gap-2 text-[10px] text-surface-400">
                  <Loader2 size={12} className="animate-spin" /> Scanning…
                </p>
              )}
              {error && (
                <p className="text-[10px] font-mono text-danger">{error}</p>
              )}

              {installs && !loading && (
                <>
                  {installs.length === 0 ? (
                    <p className="text-[10px] text-surface-500">
                      No other installs found at the default location.
                    </p>
                  ) : (
                    <div className="rounded-lg border border-surface-700/40 bg-surface-950/50 divide-y divide-surface-800/60">
                      {installs.map((i) => (
                        <InstallRow key={i.root} install={i} onRemoved={handleRemoved} />
                      ))}
                    </div>
                  )}
                </>
              )}

              {/* ── Custom path, for a non-default SPIDER_CTRL_HOME ── */}
              <div className="pt-1 space-y-1.5">
                <p className="text-[9px] text-surface-600">
                  Installed somewhere else? Check a specific path:
                </p>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Search size={11} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-surface-600" />
                    <input
                      type="text"
                      value={customPath}
                      onChange={(e) => setCustomPath(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && checkCustomPath()}
                      placeholder={
                        platform === "Windows" ? "D:\\Tools\\spider-ctrl" : "/opt/spider-ctrl"
                      }
                      aria-label="Custom install path to check"
                      autoComplete="off"
                      className="w-full pl-7 pr-2.5 py-1.5 rounded text-[10px] font-mono bg-surface-950/80 border border-surface-700/40 placeholder:text-surface-700 focus:outline-none focus:border-warning/40 text-surface-300"
                    />
                  </div>
                  <button
                    onClick={checkCustomPath}
                    disabled={!customPath.trim() || checking}
                    className="px-3 py-1.5 rounded text-[9px] font-bold tracking-[0.1em] uppercase bg-surface-800 text-surface-300 border border-surface-700/50 disabled:opacity-30 hover:bg-surface-700/60 transition-all shrink-0"
                  >
                    {checking ? <Loader2 size={11} className="animate-spin" /> : "Check"}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
