"use client";

import { useEffect, useState, useCallback } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import { AlertTriangle, ChevronDown, ChevronUp, RefreshCw, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface InputStatus {
  ok: boolean;
  reason: string | null;
  fix: string | null;
  binary: string;
  platform: string;
}

/**
 * Warn when the host cannot actually inject input.
 *
 * pyautogui fails silently when the OS refuses synthetic events, so without
 * this the app looks perfectly connected while the trackpad and keyboard do
 * nothing — which is indistinguishable from the app being broken.
 */
export default function InputWarning() {
  const { status, sendAndWait } = useWebSocket();
  const [info, setInfo] = useState<InputStatus | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const [checking, setChecking] = useState(false);

  const check = useCallback(async () => {
    setChecking(true);
    const res = (await sendAndWait("input_status")) as InputStatus | null;
    setChecking(false);
    if (res && typeof res.ok === "boolean") {
      setInfo(res);
      if (res.ok) setDismissed(false); // reset for next time
    }
  }, [sendAndWait]);

  useEffect(() => {
    if (status !== "connected") {
      setInfo(null);
      return;
    }
    check();
  }, [status, check]);

  const blocked = status === "connected" && info && !info.ok && !dismissed;

  return (
    <AnimatePresence>
      {blocked && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div className="mt-2 rounded-lg border border-warning/25 bg-warning/5 px-3 py-2.5">
            <div className="flex items-start gap-2">
              <AlertTriangle size={13} className="text-warning shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-[10px] font-bold tracking-[0.12em] uppercase text-warning">
                  Input blocked on the PC
                </p>
                <p className="text-[10px] text-surface-400 leading-relaxed mt-0.5">
                  Connected, but the trackpad and keyboard won&apos;t move
                  anything until the host grants permission.
                </p>
              </div>
              <div className="flex items-center gap-0.5 shrink-0">
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="p-1 rounded text-surface-500 hover:text-warning transition-colors"
                  aria-label={expanded ? "Hide details" : "Show how to fix"}
                >
                  {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                </button>
                <button
                  onClick={() => setDismissed(true)}
                  className="p-1 rounded text-surface-600 hover:text-surface-300 transition-colors"
                  aria-label="Dismiss"
                >
                  <X size={13} />
                </button>
              </div>
            </div>

            <AnimatePresence>
              {expanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.18 }}
                  className="overflow-hidden"
                >
                  <div className="pt-2.5 mt-2 border-t border-warning/15 space-y-2">
                    {info?.fix && (
                      <pre className="text-[9px] leading-relaxed text-surface-300 font-mono whitespace-pre-wrap break-words select-text">
                        {info.fix}
                      </pre>
                    )}
                    <button
                      onClick={check}
                      disabled={checking}
                      className="flex items-center gap-1.5 px-2.5 py-1 rounded text-[9px] font-bold tracking-[0.1em] uppercase bg-warning/10 text-warning border border-warning/25 hover:bg-warning/20 disabled:opacity-40 transition-all"
                    >
                      <RefreshCw size={10} className={checking ? "animate-spin" : ""} />
                      {checking ? "Checking" : "Re-check"}
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
