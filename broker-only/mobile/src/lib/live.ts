// Live connection to the backend WebSocket (/ws/): enquiry alerts, proposal updates, plan changes.
export type LiveEvent = { event: string; data: Record<string, unknown> };
type Listener = (e: LiveEvent) => void;

export function wsUrl(baseUrl: string, token: string): string {
  return baseUrl.replace(/^http/, 'ws').replace(/\/+$/, '') + `/ws/?token=${encodeURIComponent(token)}`;
}

export class LiveConnection {
  private ws: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private timer: ReturnType<typeof setInterval> | null = null;
  private retry = 0;
  private closed = false;

  constructor(private url: string) {}

  on(fn: Listener): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  start() {
    this.closed = false;
    const ws = new WebSocket(this.url);
    this.ws = ws;
    ws.onopen = () => {
      this.retry = 0;
      this.timer = setInterval(() => this.send({ type: 'heartbeat' }), 60_000);
    };
    ws.onmessage = (m) => {
      try {
        const e = JSON.parse(String(m.data)) as LiveEvent;
        if (e.event !== 'ack') this.listeners.forEach((fn) => fn(e));
      } catch {
        /* ignore malformed frames */
      }
    };
    ws.onclose = () => {
      if (this.timer) clearInterval(this.timer);
      if (this.closed) return;
      const delay = Math.min(30_000, 1000 * 2 ** this.retry++);
      setTimeout(() => !this.closed && this.start(), delay);
    };
  }

  send(msg: Record<string, unknown>) {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(msg));
  }

  stop() {
    this.closed = true;
    if (this.timer) clearInterval(this.timer);
    this.send({ type: 'offline' });
    this.ws?.close();
  }
}
