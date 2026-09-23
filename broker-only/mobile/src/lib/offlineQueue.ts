// Offline mutation queue for field staff (PRD OFF-10/11).
// Every action gets an idempotency key when it is recorded, so replaying the queue after a
// flaky connection can never apply the same check-in or outcome twice.
import type { Api, SyncMutation, SyncResult } from '@/api/types';

export interface KV {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
}

const KEY = 'ob.offlineQueue.v1';
const CONFLICTS = 'ob.offlineConflicts.v1';

export function newKey(): string {
  const rnd = () => Math.random().toString(36).slice(2, 10);
  return `${Date.now().toString(36)}-${rnd()}-${rnd()}`;
}

export class OfflineQueue {
  private listeners = new Set<() => void>();
  private flushing: Promise<SyncResult[]> | null = null;

  constructor(private kv: KV) {}

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  private emit() {
    this.listeners.forEach((fn) => fn());
  }

  async pending(): Promise<SyncMutation[]> {
    const raw = await this.kv.getItem(KEY);
    return raw ? (JSON.parse(raw) as SyncMutation[]) : [];
  }

  async conflicts(): Promise<SyncResult[]> {
    const raw = await this.kv.getItem(CONFLICTS);
    return raw ? (JSON.parse(raw) as SyncResult[]) : [];
  }

  async enqueue(m: Omit<SyncMutation, 'idempotency_key' | 'client_ts'> & { client_ts?: string }): Promise<SyncMutation> {
    const full: SyncMutation = { ...m, idempotency_key: newKey(), client_ts: m.client_ts ?? new Date().toISOString() };
    const q = await this.pending();
    q.push(full);
    await this.kv.setItem(KEY, JSON.stringify(q));
    this.emit();
    return full;
  }

  /** Send everything queued. Network failure keeps the queue intact; the server decides per item. */
  flush(api: Api, deviceId: string): Promise<SyncResult[]> {
    this.flushing ??= this.doFlush(api, deviceId).finally(() => (this.flushing = null));
    return this.flushing;
  }

  private async doFlush(api: Api, deviceId: string): Promise<SyncResult[]> {
    const q = await this.pending();
    if (!q.length) return [];
    const { results } = await api.sync(deviceId, q); // throws on no network: queue untouched
    const settled = new Set(results.map((r) => r.idempotency_key));
    const newConflicts = results.filter((r) => r.result === 'conflict');
    // Anything added while we were syncing stays queued.
    const remaining = (await this.pending()).filter((m) => !settled.has(m.idempotency_key));
    await this.kv.setItem(KEY, JSON.stringify(remaining));
    if (newConflicts.length) {
      const all = [...(await this.conflicts()), ...newConflicts].slice(-50);
      await this.kv.setItem(CONFLICTS, JSON.stringify(all));
    }
    this.emit();
    return results;
  }

  async clearConflicts() {
    await this.kv.setItem(CONFLICTS, '[]');
    this.emit();
  }
}
