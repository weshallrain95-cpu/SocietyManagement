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

test('demo refuses impossible flats like the server does', async () => {
  const api = createDemoApi();
  const base = { society_id: 'soc-0', bhk: '2', txn_type: 'RENT' as const, asking_rent: 20000 };
  await expect(run(api.createListing({ ...base, building: 'A Wing', unit_no: '2504' }))).rejects.toMatchObject({ status: 422 });
  await expect(run(api.createListing({ ...base, building: 'Z', unit_no: '1203' }))).rejects.toMatchObject({ status: 422 });
  const ok = await run(api.createListing({ ...base, building: 'b', unit_no: '1203' }));
  expect(ok.building).toBe('B Wing');
  // partly-known society: a warning the broker can confirm
  const other = { ...base, society_id: 'soc-2', building: 'A Wing', unit_no: '2601' };
  await expect(run(api.createListing(other))).rejects.toMatchObject({ status: 409 });
  expect((await run(api.createListing({ ...other, confirm_layout: true }))).unit_no).toBe('2601');
});

test('staff find a flat by society nickname and number, and add it to a plan', async () => {
  const api = createDemoApi();
  const r = await run(api.searchFlats('HE A-1203'));
  expect(r.results[0]).toMatchObject({ society: 'Hiranandani Estate', unit_no: '1203' });
  expect((await run(api.searchFlats('1203'))).results.every((l) => l.unit_no === '1203')).toBe(true);
  const none = await run(api.searchFlats('hiranandani estate 1504'));
  expect(none.results).toEqual([]);
  expect(none.societies[0].name).toBe('Hiranandani Estate'); // offered for "Add it now"
  const plans = await run(api.visitPlans());
  const p = plans[0];
  const after = (await run(api.planAction(p.id, 'add-stop', { listing_id: r.results[0].id }))) as { stops: { listing_id: string }[] };
  expect(after.stops.some((s) => s.listing_id === r.results[0].id)).toBe(true);
});
