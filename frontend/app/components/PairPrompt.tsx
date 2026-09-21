"use client";

import { useState, useCallback, useRef } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { ShieldCheck, Loader2, QrCode, KeyRound } from "lucide-react";
import { motion } from "framer-motion";

/** Codes are six characters from an unambiguous alphabet; see utils/pairing.py. */
const CODE_CHARS = 6;

/** Strip formatting so "abc-123" and "ABC123" are the same input. */
function normalize(raw: string): string {
  return raw.toUpperCase().replace(/[^A-Z0-9]/g, "").slice(0, CODE_CHARS);
}

function display(code: string): string {
  return code.length > 3 ? `${code.slice(0, 3)}-${code.slice(3)}` : code;
}

export default function PairPrompt() {
  const { pairWithCode, pairError } = useWebSocket();
  const [code, setCode] = useState("");
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const ready = code.length === CODE_CHARS && !busy;

  const submit = useCallback(async () => {
    if (code.length !== CODE_CHARS || busy) return;
    setBusy(true);
    const ok = await pairWithCode(code);
    setBusy(false);
    if (!ok) {
      setCode("");
      inputRef.current?.focus();
    }
  }, [code, busy, pairWithCode]);

  return (
    <div className="flex flex-col h-[100dvh] max-w-lg mx-auto px-6 justify-center hex-pattern">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="space-y-6"
      >
        {/* ── Brand ─────────────────────────── */}
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="w-12 h-12 rounded-lg border border-accent/30 bg-accent/5 flex items-center justify-center shadow-glow animate-pulse-glow">
            <ShieldCheck size={22} className="text-accent" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-[0.2em] uppercase text-accent text-glow">
              SPIDER_CTRL
            </h1>
            <p className="text-[9px] tracking-[0.15em] text-surface-500 uppercase mt-0.5">
              pair this device
            </p>
          </div>
        </div>

        {/* ── Code entry ────────────────────── */}
        <div className="glass rounded-xl p-5 space-y-4 border-glow">
          <div className="flex items-center gap-2 text-accent">
            <KeyRound size={13} />
            <p className="text-[10px] font-bold tracking-[0.15em] uppercase">
              Enter pairing code
            </p>
          </div>

          <p className="text-[10px] text-surface-400 leading-relaxed">
            Find the six-character code on your PC — it&apos;s on the setup screen
            and in the server&apos;s terminal window.
          </p>

          <input
            ref={inputRef}
            type="text"
            value={display(code)}
            onChange={(e) => setCode(normalize(e.target.value))}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder="ABC-123"
            aria-label="Pairing code"
            autoComplete="one-time-code"
            autoCorrect="off"
            autoCapitalize="characters"
            spellCheck={false}
            inputMode="text"
            className="w-full text-center py-3.5 rounded-lg text-xl font-mono tracking-[0.3em] bg-surface-950/80 border border-surface-700/40 placeholder:text-surface-700 placeholder:tracking-[0.3em] focus:outline-none focus:border-accent/40 focus:ring-1 focus:ring-accent/10 transition-all text-accent caret-accent select-text"
          />

          <button
            onClick={submit}
            disabled={!ready}
            className="w-full py-3 rounded-lg text-[11px] font-bold tracking-[0.15em] uppercase bg-accent/15 text-accent border border-accent/30 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-accent/25 active:scale-[0.98] transition-all shadow-glow-sm flex items-center justify-center gap-2"
          >
            {busy ? <Loader2 size={15} className="animate-spin" /> : null}
            {busy ? "Pairing…" : "Pair"}
          </button>

          {pairError && (
            <p className="text-[10px] font-mono text-danger bg-danger/5 border border-danger/15 rounded px-3 py-2">
              [ERR] {pairError}
            </p>
          )}
        </div>

        {/* ── QR hint ───────────────────────── */}
        <div className="flex items-start gap-2.5 px-1">
          <QrCode size={13} className="text-surface-600 shrink-0 mt-0.5" />
          <p className="text-[9px] text-surface-600 leading-relaxed">
            // faster: scan the QR code on your PC&apos;s setup screen with the
            camera app — it pairs and connects in one step, no code to type.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
