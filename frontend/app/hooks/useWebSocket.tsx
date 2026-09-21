"use client";

import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

// ── Types ───────────────────────────────────────────────────────────────────
export type ConnectionStatus = "disconnected" | "connecting" | "connected";

interface WSContextValue {
  status: ConnectionStatus;
  serverIp: string;
  connect: (ip: string, token?: string) => void;
  disconnect: () => void;
  send: (action: string, payload?: Record<string, unknown>) => void;
  sendAndWait: (
    action: string,
    payload?: Record<string, unknown>
  ) => Promise<unknown>;
  lastError: string | null;
  pcInfo: Record<string, unknown> | null;
  isDeployed: boolean;
  /** Pairing token for this PC, or null when this device has never paired. */
  token: string | null;
  /** True when the server is serving us but we have no token to offer it. */
  needsPairing: boolean;
  pairError: string | null;
  /** Trade the six-character code shown on the PC for the real token. */
  pairWithCode: (code: string) => Promise<boolean>;
  forgetPairing: () => void;
}

const WSContext = createContext<WSContextValue | null>(null);

// ── Provider ────────────────────────────────────────────────────────────────
const SERVER_PORT = 8765;
const RECONNECT_DELAY = 3000;
const REQUEST_TIMEOUT = 35000;
const TOKEN_KEY = "spiderctrl_token";

/** Close code the server uses to say "your token is no good". */
const WS_POLICY_VIOLATION = 1008;

/**
 * Detect if running on the Vercel-deployed site (or any external host).
 * When deployed, we can’t connect via WebSocket — we redirect instead.
 */
function checkIsDeployed(): boolean {
  if (typeof window === "undefined") return false;
  const { hostname, port } = window.location;
  if (port === String(SERVER_PORT)) return false;
  if (hostname === "localhost" || hostname === "127.0.0.1") return false;
  return true;
}

/**
 * Detect if the frontend is being served from the PC server itself.
 * If so, we can auto-connect using the page's hostname (no manual IP needed).
 */
function getAutoServerIp(): string | null {
  if (typeof window === "undefined") return null;
  const { hostname, port } = window.location;
  // If served from the Python server (port 8765), use same hostname
  if (port === String(SERVER_PORT)) return hostname;
  return null;
}

// ── Token storage ───────────────────────────────────────────────────────────
function loadToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function saveToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Private browsing — the token still works for this page load.
  }
}

function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // ignore
  }
}

/**
 * Take the token out of the address bar once we've stored it.
 *
 * Scanning the QR lands on /?t=<token>, and leaving it there means the
 * credential sits in history and in anything the user shares or screenshots.
 */
function stripTokenFromUrl(): void {
  try {
    const url = new URL(window.location.href);
    if (!url.searchParams.has("t")) return;
    url.searchParams.delete("t");
    const rest = url.searchParams.toString();
    window.history.replaceState(
      {},
      "",
      url.pathname + (rest ? `?${rest}` : "") + url.hash
    );
  } catch {
    // ignore
  }
}

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [serverIp, setServerIp] = useState("");
  const [lastError, setLastError] = useState<string | null>(null);
  const [pcInfo, setPcInfo] = useState<Record<string, unknown> | null>(null);
  const [isDeployed, setIsDeployed] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [pairError, setPairError] = useState<string | null>(null);
  // Gates anything that reads window/localStorage, so the static export and
  // the first client render agree.
  const [booted, setBooted] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const manualDisconnectRef = useRef(false);
  const pendingRef = useRef<Map<string, (data: unknown) => void>>(new Map());
  const idCounterRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();
  // Mirrors `token` so reconnect callbacks don't close over a stale value.
  const tokenRef = useRef<string | null>(null);
  const autoConnectedRef = useRef(false);

  const applyToken = useCallback((next: string | null) => {
    tokenRef.current = next;
    setToken(next);
    if (next) saveToken(next);
    else clearToken();
  }, []);

  // Detect deployed state and pick up a token on mount
  useEffect(() => {
    setIsDeployed(checkIsDeployed());
    const params = new URLSearchParams(window.location.search);
    const fromUrl = params.get("t");
    if (fromUrl) {
      applyToken(fromUrl);
      stripTokenFromUrl();
    } else {
      const stored = loadToken();
      tokenRef.current = stored;
      setToken(stored);
    }
    setBooted(true);
  }, [applyToken]);

  const cleanup = useCallback(() => {
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.onmessage = null;
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const connect = useCallback(
    (ip: string, tokenOverride?: string) => {
      cleanup();
      manualDisconnectRef.current = false;
      setServerIp(ip);
      setLastError(null);

      const authToken = tokenOverride ?? tokenRef.current;
      if (!authToken) {
        setStatus("disconnected");
        setLastError("Not paired with this PC yet.");
        return;
      }

      setStatus("connecting");

      // If the IP already contains a port (e.g. "192.168.1.5:8765"), use as-is
      // Otherwise append the default server port
      const host = ip.includes(":") ? ip : `${ip}:${SERVER_PORT}`;
      // An https page can only open wss:// — ws:// is blocked as mixed content.
      const scheme = window.location.protocol === "https:" ? "wss" : "ws";
      const url = `${scheme}://${host}/ws?t=${encodeURIComponent(authToken)}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        setLastError(null);
        setPairError(null);
        // Request system info on connect
        const id = `__init_${Date.now()}`;
        ws.send(JSON.stringify({ action: "system_info", id }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          // Handle pending request-response. A failed handler comes back as
          // {ok: false, error}, with no `data` — pass the error through so
          // callers can show it rather than silently receiving undefined.
          if (data.id && pendingRef.current.has(data.id)) {
            const settle = pendingRef.current.get(data.id)!;
            pendingRef.current.delete(data.id);
            settle(data.ok === false ? { error: data.error } : data.data);
          }
          // Capture system info
          if (data.id?.startsWith("__init_") && data.data) {
            setPcInfo(data.data);
          }
        } catch {
          // ignore
        }
      };

      ws.onclose = (event) => {
        setStatus("disconnected");

        // The server rejected our token. Retrying can only fail the same way,
        // so drop it and fall back to the pairing screen.
        if (event.code === WS_POLICY_VIOLATION) {
          applyToken(null);
          autoConnectedRef.current = false;
          setLastError("Pairing rejected — pair this device again.");
          return;
        }

        // Only auto-reconnect when served from the PC server (same origin)
        if (ip && !manualDisconnectRef.current && !checkIsDeployed()) {
          reconnectTimerRef.current = setTimeout(() => connect(ip), RECONNECT_DELAY);
        }
      };

      ws.onerror = () => {
        setLastError("Connection failed. Check the IP and ensure the server is running.");
      };
    },
    [cleanup, applyToken]
  );

  const disconnect = useCallback(() => {
    manualDisconnectRef.current = true;
    autoConnectedRef.current = true; // don't immediately auto-reconnect
    cleanup();
    setStatus("disconnected");
    setServerIp("");
    setPcInfo(null);
    setLastError(null);
  }, [cleanup]);

  /** Forget this PC entirely — drops the link and the stored token. */
  const forgetPairing = useCallback(() => {
    manualDisconnectRef.current = true;
    cleanup();
    applyToken(null);
    autoConnectedRef.current = false;
    setStatus("disconnected");
    setServerIp("");
    setPcInfo(null);
    setLastError(null);
    setPairError(null);
  }, [cleanup, applyToken]);

  const pairWithCode = useCallback(
    async (code: string): Promise<boolean> => {
      setPairError(null);
      const trimmed = code.trim();
      if (!trimmed) {
        setPairError("Enter the code shown on your PC.");
        return false;
      }
      try {
        // Same origin: this only runs on the page the PC server itself serves.
        const res = await fetch("/pair/claim", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: trimmed }),
        });
        if (!res.ok) {
          setPairError(
            res.status === 403
              ? "Wrong or expired code. Check the PC for a fresh one."
              : `Pairing failed (${res.status}).`
          );
          return false;
        }
        const data = await res.json();
        if (!data?.token) {
          setPairError("Server did not return a token.");
          return false;
        }
        applyToken(data.token);
        autoConnectedRef.current = true;
        connect(window.location.hostname, data.token);
        return true;
      } catch {
        setPairError("Could not reach the server.");
        return false;
      }
    },
    [applyToken, connect]
  );

  const send = useCallback((action: string, payload?: Record<string, unknown>) => {
    const ws = wsRef.current;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action, payload }));
    }
  }, []);

  const sendAndWait = useCallback(
    (action: string, payload?: Record<string, unknown>) => {
      return new Promise<unknown>((resolve) => {
        const ws = wsRef.current;
        if (ws?.readyState !== WebSocket.OPEN) {
          resolve(null);
          return;
        }
        const id = `req_${++idCounterRef.current}_${Date.now()}`;

        // Timeout after 35 s (covers terminal commands with 30s default timeout)
        const timer = setTimeout(() => {
          pendingRef.current.delete(id);
          resolve(null);
        }, REQUEST_TIMEOUT);

        pendingRef.current.set(id, (data) => {
          clearTimeout(timer);
          resolve(data);
        });
        ws.send(JSON.stringify({ action, payload, id }));
      });
    },
    []
  );

  // Cleanup on unmount
  useEffect(() => cleanup, [cleanup]);

  // Auto-connect when served from the Python server and we already hold a token
  useEffect(() => {
    if (!booted || autoConnectedRef.current) return;
    const autoIp = getAutoServerIp();
    if (autoIp && token && status === "disconnected") {
      autoConnectedRef.current = true;
      connect(autoIp, token);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [booted, token]);

  const needsPairing =
    booted && getAutoServerIp() !== null && !token && status !== "connected";

  return (
    <WSContext.Provider
      value={{
        status,
        serverIp,
        connect,
        disconnect,
        send,
        sendAndWait,
        lastError,
        pcInfo,
        isDeployed,
        token,
        needsPairing,
        pairError,
        pairWithCode,
        forgetPairing,
      }}
    >
      {children}
    </WSContext.Provider>
  );
}

// ── Hook ────────────────────────────────────────────────────────────────────
export function useWebSocket() {
  const ctx = useContext(WSContext);
  if (!ctx) throw new Error("useWebSocket must be used inside WebSocketProvider");
  return ctx;
}
