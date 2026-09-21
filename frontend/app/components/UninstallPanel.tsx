"use client";

import { useState, useCallback, useEffect } from "react";
import { Trash2, AlertTriangle, Loader2, Check, ChevronDown, ChevronUp } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const SERVER_PORT = 8765;

function apiBase(): string {
  if (typeof window === "undefined") return "";
  return window.location.port === String(SERVER_PORT)
    ? ""
    : `http://127.0.0.1:${SERVER_PORT}`;
}

interface PlanItem {
  path: string;
  label: string;
  bytes: number;
}

interface Plan {
  mode: "full" | "artifacts";
  managed: boolean;
  root: string;
  items: PlanItem[];
  total_bytes: number;
  confirm_phrase: string;
  blocked: string | null;
  notes: string[];
}

function mb(bytes: number): string {
  if (bytes >= 1e9) return `${(bytes / 1e9).toFixed(1)} GB`;
  if (bytes >= 1e6) return `${Math.round(bytes / 1e6)} MB`;
  if (bytes >= 1e3) return `${Math.round(bytes / 1e3)} KB`;
  return `${bytes} B`;
}

/**
 * Danger zone: remove the server from this machine.
 *
 * Collapsed by default and gated behind a typed phrase, because it is
 * irreversible. The plan is fetched from the host and shown in full first —
 * nobody should have to guess what a delete button is about to take.
 */
export default function UninstallPanel() {
  const [open, setOpen] = useState(false);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [loading, setLoading] = useState(false);
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState<{ freed: number; failed: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/uninstall/plan`, { cache: "no-store" });
      if (!res.ok) throw new Error(String(res.status));
      setPlan(await res.json());
    } catch {
      setError("Could not reach the server on this machine.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open && !plan) load();
  }, [open, plan, load]);

  const run = useCallback(async () => {
    if (!plan || confirm !== plan.confirm_phrase) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase()}/uninstall`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirm }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        setError(data.error ?? `Uninstall failed (${res.status}).`);
      } else {
        setDone({ freed: data.freed_bytes ?? 0, failed: (data.failed ?? []).length });
      }
    } catch {
      // The server kills itself right after replying, so a dropped
      // connection here is the expected ending, not a failure.
      setDone({ freed: plan.total_bytes, failed: 0 });
    } finally {
      setBusy(false);
    }
  }, [plan, confirm]);

  if (done) {
    return (
      <div className="mt-6 rounded-xl border border-accent/20 bg-accent/5 px-5 py-4">
        <div className="flex items-center gap-2 text-accent">
          <Check size={14} />
          <p className="text-[11px] font-bold tracking-[0.15em] uppercase">Removed</p>
        </div>
        <p className="text-[10px] text-surface-400 mt-1.5 leading-relaxed">
          Freed about {mb(done.freed)}. The server has stopped.
          {done.failed > 0 && " Some files could not be deleted — check the terminal."}
        </p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-[9px] font-mono tracking-[0.1em] uppercase text-surface-600 hover:text-danger transition-colors"
      >
        <Trash2 size={10} />
        // remove spider_ctrl from this pc
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
            <div className="mt-3 rounded-xl border border-danger/25 bg-danger/5 p-5 space-y-4">
              <div className="flex items-center gap-2 text-danger">
                <AlertTriangle size={14} />
                <h3 className="text-[11px] font-bold tracking-[0.15em] uppercase text-glow-danger">
                  Danger zone
                </h3>
              </div>

              {loading && (
                <p className="flex items-center gap-2 text-[10px] text-surface-400">
                  <Loader2 size={12} className="animate-spin" /> Working out what would go…
                </p>
              )}

              {error && (
                <p className="text-[10px] font-mono text-danger bg-danger/5 border border-danger/15 rounded px-3 py-2">
                  [ERR] {error}
                </p>
              )}

              {plan?.blocked && (
                <p className="text-[10px] font-mono text-warning">
                  Refused: {plan.blocked}
                </p>
              )}

              {plan && !plan.blocked && (
                <>
                  <div className="space-y-1">
                    <p className="text-[9px] tracking-[0.15em] uppercase text-surface-500">
                      // will be deleted from {plan.root}
                    </p>
                    <div className="rounded-lg bg-surface-950/70 border border-surface-700/40 divide-y divide-surface-800/60">
                      {plan.items.length === 0 && (
                        <p className="px-3 py-2 text-[10px] text-surface-500">
                          Nothing left to remove.
                        </p>
                      )}
                      {plan.items.map((i) => (
                        <div key={i.path} className="flex items-center justify-between px-3 py-1.5 gap-3">
                          <code className="text-[10px] font-mono text-surface-300 truncate">
                            {i.label}
                          </code>
                          <span className="text-[9px] font-mono text-surface-500 shrink-0">
                            {mb(i.bytes)}
                          </span>
                        </div>
                      ))}
                    </div>
                    {plan.items.length > 0 && (
                      <p className="text-[9px] font-mono text-surface-500 text-right">
                        total {mb(plan.total_bytes)}
                      </p>
                    )}
                  </div>

                  {plan.notes.length > 0 && (
                    <ul className="space-y-1">
                      {plan.notes.map((n) => (
                        <li key={n} className="text-[9px] text-surface-500 leading-relaxed">
                          · {n}
                        </li>
                      ))}
                    </ul>
                  )}

                  {plan.items.length > 0 && (
                    <div className="space-y-2 pt-1">
                      <p className="text-[10px] text-surface-400">
                        This cannot be undone. Type{" "}
                        <code className="bg-surface-800 px-1.5 py-0.5 rounded text-danger border border-surface-700/40">
                          {plan.confirm_phrase}
                        </code>{" "}
                        to confirm.
                      </p>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={confirm}
                          onChange={(e) => setConfirm(e.target.value)}
                          placeholder={plan.confirm_phrase}
                          aria-label="Type the confirmation phrase"
                          autoComplete="off"
                          className="flex-1 px-3 py-2 rounded-lg text-xs font-mono bg-surface-950/80 border border-surface-700/40 placeholder:text-surface-700 focus:outline-none focus:border-danger/40 focus:ring-1 focus:ring-danger/10 transition-all text-danger select-text"
                        />
                        <button
                          onClick={run}
                          disabled={confirm !== plan.confirm_phrase || busy}
                          className="px-4 py-2 rounded-lg text-[10px] font-bold tracking-[0.12em] uppercase bg-danger/15 text-danger border border-danger/30 disabled:opacity-25 disabled:cursor-not-allowed hover:bg-danger/25 active:scale-95 transition-all flex items-center gap-1.5"
                        >
                          {busy ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                          {busy ? "Removing" : "Delete"}
                        </button>
                      </div>
                    </div>
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
