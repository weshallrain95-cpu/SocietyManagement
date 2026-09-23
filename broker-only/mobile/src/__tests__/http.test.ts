import type { Tokens } from '@/api/types';
import { ApiError, createHttpApi } from '@/api/http';

function store(initial: Tokens | null) {
  let t = initial;
  return { get: () => t, set: (n: Tokens | null) => (t = n), peek: () => t };
}
const tokens: Tokens = { access: 'old', refresh: 'r1', role: 'broker_principal', org: 'o' };
const res = (status: number, body: unknown) => ({ ok: status < 400, status, text: async () => JSON.stringify(body), json: async () => body });

afterEach(() => jest.restoreAllMocks());

test('sends the bearer token and parses JSON', async () => {
  const f = jest.spyOn(globalThis, 'fetch').mockResolvedValue(res(200, [{ id: 'l1' }]) as never);
  const api = createHttpApi('http://x:8000/', store(tokens));
  expect(await api.listings({ status: 'AVAILABLE' })).toEqual([{ id: 'l1' }]);
  const [url, init] = f.mock.calls[0] as [string, RequestInit];
  expect(url).toBe('http://x:8000/v1/listings?status=AVAILABLE');
  expect((init.headers as Record<string, string>).Authorization).toBe('Bearer old');
});

test('refreshes an expired access token once and retries', async () => {
  const s = store(tokens);
  const f = jest
    .spyOn(global, 'fetch')
    .mockResolvedValueOnce(res(401, { detail: 'expired' }) as never)
    .mockResolvedValueOnce(res(200, { access: 'new', refresh: 'r2' }) as never)
    .mockResolvedValueOnce(res(200, { id: 'me' }) as never);
  const api = createHttpApi('http://x', s);
  expect(await api.me()).toEqual({ id: 'me' });
  expect(s.peek()?.access).toBe('new');
  expect(((f.mock.calls[2][1] as RequestInit).headers as Record<string, string>).Authorization).toBe('Bearer new');
});

test('server validation errors become readable messages', async () => {
  jest.spyOn(globalThis, 'fetch').mockResolvedValue(res(400, { asking_rent: ['Rent is required for a rental listing'] }) as never);
  const api = createHttpApi('http://x', store(tokens));
  await expect(api.createListing({} as never)).rejects.toThrow('asking rent: Rent is required for a rental listing');
});

test('no network gives a clear error', async () => {
  jest.spyOn(globalThis, 'fetch').mockRejectedValue(new TypeError('Network request failed'));
  const api = createHttpApi('http://x', store(tokens));
  const err = await api.leads().catch((e) => e);
  expect(err).toBeInstanceOf(ApiError);
  expect(err.status).toBe(0);
});
