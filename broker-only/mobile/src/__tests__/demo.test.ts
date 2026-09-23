import { createDemoApi } from '@/api/demo';

jest.useFakeTimers();
const run = async <T,>(p: Promise<T>) => {
  jest.runAllTimers();
  return p;
};

test('demo matching respects pets and budget, and explains why', async () => {
  const api = createDemoApi();
  const all = await run(api.match('req-1', true));
  const fitting = all.results.filter((r) => !r.excluded);
  expect(fitting.length).toBeGreaterThan(0);
  expect(fitting.every((r) => (r.listing.asking_rent ?? 0) <= 25000 * 1.1)).toBe(true);
  const noPets = all.results.find((r) => r.listing.id === 'lst-2')!;
  expect(noPets.excluded).toBe(true);
  expect(noPets.explanation.find((c) => c.key === 'pets_allowed')?.result).toBe('fail');
});

test('re-opening a rented flat needs the owner unless recorded on their behalf', async () => {
  const api = createDemoApi();
  await run(api.reportStatus('lst-1', { state: 'LET' }));
  expect((await run(api.reportStatus('lst-1', { state: 'AVAILABLE' }))).state).toBe('AVAILABLE_UNCONFIRMED');
  expect((await run(api.reportStatus('lst-1', { state: 'AVAILABLE', on_behalf_of_owner: true }))).state).toBe('AVAILABLE');
});

test('capturing the same number twice returns the same customer', async () => {
  const api = createDemoApi();
  const a = await run(api.captureCustomer({ phone: '9811122233', source: 'walk_in' }));
  const b = await run(api.captureCustomer({ phone: '+91 98111 22233', source: 'phone_call' }));
  expect(a.id).toBe(b.id);
});
