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
  expect(none).toEqual({ results: [], unit_no: '1504', wing: '' }); // not in the broker's list: nothing offered
  const plans = await run(api.visitPlans());
  const p = plans[0];
  const after = (await run(api.planAction(p.id, 'add-stop', { listing_id: r.results[0].id }))) as { stops: { listing_id: string }[] };
  expect(after.stops.some((s) => s.listing_id === r.results[0].id)).toBe(true);
});

test('owner removes a broker; that broker loses the flat until allowed again', async () => {
  const api = createDemoApi();
  expect((await run(api.verifyOtp('9820020000', '123456'))).role).toBe('owner');
  const [flat] = await run(api.ownerFlats());
  expect(flat.brokers.map((b) => b.name)).toContain('Demo Realty Dhokali');
  expect((await run(api.listing('lst-1'))).media?.length).toBe(3); // owner photos reach the broker holding the flat
  await run(api.setBrokerAllowed(flat.id, 'org-demo', false, 'not responsive'));
  const l = await run(api.listing('lst-1'));
  expect(l.owner_withdrew).toBe(true);
  expect(l.media).toEqual([]);
  await run(api.askOwnerBack('lst-1', 'Sorry — new staff member assigned'));
  expect((await run(api.ownerFlat(flat.id))).brokers.find((b) => b.org_id === 'org-demo')?.asked_back).toMatch(/new staff/);
  await run(api.setBrokerAllowed(flat.id, 'org-demo', true));
  expect((await run(api.listing('lst-1'))).owner_withdrew).toBe(false);
});

test('an invitation needs the owner’s allow tick; the broker accepts it into their own flats', async () => {
  const api = createDemoApi();
  const [flat] = await run(api.ownerFlats());
  await expect(run(api.inviteBroker(flat.id, 'org-shree', false))).rejects.toMatchObject({ status: 400 });
  expect((await run(api.inviteBroker(flat.id, 'org-shree', true))).state).toBe('pending');
  const [inv] = await run(api.ownerInvites());
  const r = await run(api.respondInvite(inv.id, 'accept'));
  const l = await run(api.listing(r.listing_id!));
  expect(l.owner_appointed).toBe(true);
  expect(l.society).toBe('Hiranandani Meadows');
});

test('broker photos wait for the owner; the owner approves what goes live', async () => {
  const api = createDemoApi();
  const up = await run(api.uploadListingMedia('lst-1', { uri: 'blob:x', name: 'hall.jpg', type: 'image/jpeg' }));
  expect(up.state).toBe('pending');
  expect((await run(api.listing('lst-1'))).my_pending_media?.length).toBe(1);
  const [flat] = await run(api.ownerFlats());
  const f = await run(api.ownerFlat(flat.id));
  expect(f.pending_media?.[0].uploaded_by).toBe('Demo Realty Dhokali');
  const after = await run(api.reviewMedia(up.id, true));
  expect(after.media?.length).toBe(4);
  const l = await run(api.listing('lst-1'));
  expect(l.media?.length).toBe(4);
  expect(l.my_pending_media).toEqual([]);
});

test('a broadcast reaches customers in the app and lists the rest for a WhatsApp invite', async () => {
  const api = createDemoApi();
  const pre = await run(api.broadcastPreview({ kind: 'new_flat', listing_id: 'lst-1' }));
  expect(pre.text).toMatch(/^New 2 BHK for rent in Hiranandani Estate/);
  expect(pre.text).not.toMatch(/1203/);
  const r = await run(api.sendBroadcast({ kind: 'new_flat', listing_id: 'lst-1' }));
  expect(r.delivered_in_app).toBe(2);
  expect(r.invite[0].whatsapp_url).toMatch(/^https:\/\/wa\.me\/91\d{10}\?text=/);
  const ups = await run(api.myUpdates());
  expect(ups[0].org).toBe('Demo Realty Dhokali');
  await run(api.muteBroker('org-demo', true));
  expect((await run(api.myUpdates())).find((u) => u.org_id === 'org-demo')?.muted).toBe(true);
});
