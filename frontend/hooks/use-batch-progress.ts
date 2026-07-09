"use client";

import { useEffect, useRef, useState } from "react";

import { getBatchProgress } from "@/lib/batch";
import type { BatchProgress } from "@/types/batch";

const TERMINAL = new Set(["completed", "completed_with_errors", "failed", "canceled"]);

function websocketUrl(batchId: string): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const url = new URL(apiUrl);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = `/ws/batch/${batchId}/`;
  url.search = "";
  return url.toString();
}

export function useBatchProgress(batchId: string | null, initial?: BatchProgress | null) {
  const [progress, setProgress] = useState<BatchProgress | null>(initial ?? null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reconnectAttempt = useRef(0);
  const latestProgress = useRef<BatchProgress | null>(initial ?? null);

  useEffect(() => {
    if (!initial) return;
    const timeout = window.setTimeout(() => {
      latestProgress.current = initial;
      setProgress(initial);
    }, 0);
    return () => window.clearTimeout(timeout);
  }, [initial]);

  useEffect(() => {
    if (!batchId) return;
    const activeBatchId = batchId;
    let socket: WebSocket | null = null;
    let reconnectTimer: number | null = null;
    let pollTimer: number | null = null;
    let stopped = false;

    async function poll() {
      try {
        const next = await getBatchProgress(activeBatchId);
        if (!stopped) {
          setProgress(next);
          latestProgress.current = next;
          setError(null);
        }
        if (TERMINAL.has(next.status) && pollTimer) {
          window.clearInterval(pollTimer);
          pollTimer = null;
        }
      } catch {
        if (!stopped) setError("Could not refresh batch progress.");
      }
    }

    function startPolling() {
      void poll();
      if (!pollTimer) {
        pollTimer = window.setInterval(() => void poll(), 3000);
      }
    }

    function connect() {
      socket = new WebSocket(websocketUrl(activeBatchId));
      socket.onopen = () => {
        reconnectAttempt.current = 0;
        setIsConnected(true);
        setError(null);
      };
      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as { payload?: BatchProgress };
          if (message.payload) {
            latestProgress.current = message.payload;
            setProgress(message.payload);
          }
        } catch {
          setError("Received an invalid batch progress event.");
        }
      };
      socket.onerror = () => {
        setError("Live progress disconnected. Polling is active.");
      };
      socket.onclose = () => {
        setIsConnected(false);
        startPolling();
        if (!stopped && !progressHasEnded(latestProgress.current)) {
          const delay = Math.min(10000, 1000 * 2 ** reconnectAttempt.current);
          reconnectAttempt.current += 1;
          reconnectTimer = window.setTimeout(connect, delay);
        }
      };
    }

    connect();
    startPolling();

    return () => {
      stopped = true;
      if (socket) socket.close();
      if (reconnectTimer) window.clearTimeout(reconnectTimer);
      if (pollTimer) window.clearInterval(pollTimer);
    };
  }, [batchId]);

  return { progress, setProgress, isConnected, error };
}

function progressHasEnded(progress: BatchProgress | null): boolean {
  return progress ? TERMINAL.has(progress.status) : false;
}
