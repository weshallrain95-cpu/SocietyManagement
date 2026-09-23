import type { Api, SyncMutation } from '@/api/types';
import { OfflineQueue, type KV } from '@/lib/offlineQueue';
import { overlay } from '@/lib/useOfflineDay';

function memoryKV(): KV & { data: Record<string, string> } {
  const data: Record<string, string> = {};
  return { data, getItem: async (k) => data[k] ?? null, setItem: async (k, v) => void (data[k] = v) };
}

function fakeApi(handler: (m: SyncMutation[]) => Promise<ReturnType<Api['sync']> extends Promise<infer R> ? R : never>): Api {
  return { sync: (_d: string, m: SyncMutation[]) => handler(m) } as unknown as Api;
}

test('each queued action gets a unique idempotency key and survives a failed sync', async () => {
  const q = new OfflineQueue(memoryKV());
  const a = await q.enqueue({ entity: 'checkin', stop_id: 's1' });
  const b = await q.enqueue({ entity: 'outcome', stop_id: 's1', outcome: 'liked' });
  expect(a.idempotency_key).not.toEqual(b.idempotency_key);
  const offline = fakeApi(() => Promise.reject(new Error('no network')));
  await expect(q.flush(offline, 'dev')).rejects.toThrow('no network');
  expect(await q.pending()).toHaveLength(2);
});

test('applied and duplicate items leave the queue; conflicts are kept for the user to see', async () => {
  const q = new OfflineQueue(memoryKV());
  const a = await q.enqueue({ entity: 'checkin', stop_id: 's1' });
  const b = await q.enqueue({ entity: 'outcome', stop_id: 's2', outcome: 'rejected' });
  const api = fakeApi(async () => ({
    results: [
      { idempotency_key: a.idempotency_key, result: 'applied', detail: {} },
      { idempotency_key: b.idempotency_key, result: 'conflict', detail: { reason: 'stop_removed_by_broker' } },
    ],
    plans: [],
  }));
  await q.flush(api, 'dev');
  expect(await q.pending()).toHaveLength(0);
  expect((await q.conflicts())[0].detail.reason).toBe('stop_removed_by_broker');
});

test('actions recorded while a sync is in flight are not lost', async () => {
  const q = new OfflineQueue(memoryKV());
  const a = await q.enqueue({ entity: 'checkin', stop_id: 's1' });
  let release!: () => void;
  const gate = new Promise<void>((r) => (release = r));
  const api = fakeApi(async () => {
    await gate;
    return { results: [{ idempotency_key: a.idempotency_key, result: 'applied', detail: {} }], plans: [] };
  });
  const flushing = q.flush(api, 'dev');
  await q.enqueue({ entity: 'outcome', stop_id: 's1', outcome: 'liked' });
  release();
  await flushing;
  const left = await q.pending();
  expect(left).toHaveLength(1);
  expect(left[0].outcome).toBe('liked');
});

test('concurrent flushes share one request', async () => {
  const q = new OfflineQueue(memoryKV());
  await q.enqueue({ entity: 'checkin', stop_id: 's1' });
  const sync = jest.fn(async (_d: string, m: SyncMutation[]) => ({ results: m.map((x) => ({ idempotency_key: x.idempotency_key, result: 'applied' as const, detail: {} })), plans: [] }));
  const api = { sync } as unknown as Api;
  await Promise.all([q.flush(api, 'd'), q.flush(api, 'd')]);
  expect(sync).toHaveBeenCalledTimes(1);
});

test('overlay shows queued check-ins and the latest outcome immediately', () => {
  const plans = [{ id: 'p', stops: [{ id: 's1', checkin_at: null, outcome: '' }] }] as never;
  const pending: SyncMutation[] = [
    { idempotency_key: '1', entity: 'checkin', stop_id: 's1', client_ts: '2026-10-03T05:35:00Z' },
    { idempotency_key: '2', entity: 'outcome', stop_id: 's1', client_ts: 't', outcome: 'rejected' },
    { idempotency_key: '3', entity: 'outcome', stop_id: 's1', client_ts: 't', outcome: 'liked' },
  ];
  const [p] = overlay(plans, pending);
  expect(p.stops[0].checkin_at).toBe('2026-10-03T05:35:00Z');
  expect(p.stops[0].outcome).toBe('liked');
});
