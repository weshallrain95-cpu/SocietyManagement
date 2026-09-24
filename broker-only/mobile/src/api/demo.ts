// In-app demo backend: the full Api contract over in-memory Thane West sample data.
// Used for the online preview (no server access needed) and for UI development.
// Business rules mirror the backend in simplified form; the backend remains the source of truth.
import type {
  Api, AttributeDef, Chip, Customer, Lead, Listing, MatchResult, Requirement, SocietyCandidate, StaffMember,
  TimelineItem, Tokens, UnitState, VisitPlan, VisitStop, Wing,
} from './types';
import { indiaDate } from '@/lib/format';
import { checkFlat, parseUnitNo } from '@/lib/layout';
import { ApiError } from './http';

const wait = (ms = 250) => new Promise((r) => setTimeout(r, ms));
let seq = 1000;
const id = (p: string) => `${p}-${++seq}`;
const now = () => new Date().toISOString();
const today = () => indiaDate();

const SOCIETIES: SocietyCandidate[] = [
  ['Hiranandani Estate', 'Hiranandani Estate', 19.2585, 72.969],
  ['Rodas Enclave', 'Hiranandani Estate', 19.26, 72.966],
  ['Lodha Amara', 'Kolshet', 19.223, 72.993],
  ['Kalpataru Parkcity', 'Kolshet', 19.225, 72.99],
  ['Dosti Imperia', 'Manpada', 19.234, 72.974],
  ['Tulsi Dham', 'Manpada', 19.233, 72.9765],
  ['Vasant Vihar', 'Vasant Vihar', 19.223, 72.963],
  ['Rustomjee Urbania', 'Majiwada', 19.213, 72.983],
  ['Puranik City', 'Kasarvadavali', 19.264, 72.974],
  ['Hiranandani Meadows', 'Pokhran Road', 19.2235, 72.969],
].map(([name, locality, lat, lng], i) => ({
  society_id: `soc-${i}`, name: name as string, locality: locality as string, status: 'active' as const, score: 1,
  location: { lat: lat as number, lng: lng as number },
}));

// Wing layouts: Hiranandani Estate is fully surveyed (verified, every wing listed); the rest are partly known.
const layout = (floors: number, perFloor: number, verified: boolean, skip: number[] = []): Wing['layout'] => ({
  floors_total: floors, lowest_floor: 1, units_per_floor: perFloor, skip_floors: skip, extra_unit_nos: [], verified, source: verified ? 'survey' : 'broker',
});
const WINGS: Record<string, { wings: Wing[]; wings_complete: boolean }> = Object.fromEntries(
  SOCIETIES.map((s, i) => [
    s.society_id,
    i === 0
      ? { wings: ['A', 'B', 'C'].map((w) => ({ id: `bld-${i}-${w}`, name: `${w} Wing`, layout: layout(20, 4, true, [11]) })), wings_complete: true }
      : { wings: [{ id: `bld-${i}-A`, name: 'A Wing', layout: layout(22, 6, false) }], wings_complete: false },
  ]),
);

// Rough stand-in for the server's fuzzy society search (aliases, typos): a few nicknames plus prefix matching.
const NICKNAMES: Record<string, string> = { he: 'Hiranandani Estate', hm: 'Hiranandani Meadows', kpc: 'Kalpataru Parkcity' };
function findSocieties(q: string): SocietyCandidate[] {
  const n = q.toLowerCase().replace(/[^a-z]/g, '');
  const nick = NICKNAMES[n];
  if (nick) return SOCIETIES.filter((s) => s.name === nick);
  if (n.length < 2) return [];
  return SOCIETIES.filter((s) => s.name.toLowerCase().replace(/[^a-z]/g, '').includes(n.slice(0, 5)) || n.includes(s.name.toLowerCase().replace(/[^a-z]/g, '').slice(0, 6)));
}

const LABEL: Record<UnitState, string> = {
  UNKNOWN: 'Status unknown', AVAILABLE: 'Available for rent', AVAILABLE_UNCONFIRMED: 'Available – not yet confirmed by owner',
  ON_HOLD: 'On hold (under negotiation)', LET: 'Rented out', SOLD: 'Sold', OFF_MARKET: 'Off market',
};

function mkListing(i: number, soc: SocietyCandidate, unit: string, bhk: number, rent: number, state: UnitState, attrs: Record<string, unknown>): Listing {
  return {
    id: `lst-${i}`, txn_type: 'RENT', unit_id: `unit-${i}`, society: soc.name, society_id: soc.society_id, building: 'A Wing',
    unit_no: unit, floor: Math.floor(Number(unit) / 100) || 0, bhk, asking_rent: rent, asking_price: null, deposit: rent * 3,
    available_from: today(), status: state, status_label: LABEL[state], last_confirmed_at: now(), origin: 'manual',
    visibility: 'private', stale: i % 5 === 0, maintenance: 3500, negotiable: true, brokerage_terms: '1 month rent',
    owner_name: 'Owner (demo)', owner_phone: '+91 98190 •••••', private_notes: '',
    keys: { holder_type: i % 3 === 0 ? 'owner' : 'office', holder_user_id: null, instructions: 'Drawer 3', needs_handover: false },
    attributes: Object.fromEntries(Object.entries(attrs).map(([k, v]) => [k, { value: v, source: 'broker', disputed: false }])),
  };
}

const listings: Listing[] = [
  mkListing(1, SOCIETIES[0], '1203', 2, 24000, 'AVAILABLE', { pets_allowed: 'all pets', furnishing: 'semi-furnished', furn_gas_stove: true, furn_kitchen_cabinet: true, lift: true }),
  mkListing(2, SOCIETIES[0], '1204', 2, 22000, 'AVAILABLE_UNCONFIRMED', { pets_allowed: 'no', furnishing: 'unfurnished', lift: true }),
  mkListing(3, SOCIETIES[1], '802', 3, 38000, 'AVAILABLE', { pets_allowed: 'case-by-case', furnishing: 'fully furnished', lift: true }),
  mkListing(4, SOCIETIES[2], '1501', 2, 26500, 'AVAILABLE', { pets_allowed: 'small dogs', furnishing: 'semi-furnished', furn_gas_stove: true }),
  mkListing(5, SOCIETIES[3], '704', 1, 16000, 'ON_HOLD', { pets_allowed: 'no', furnishing: 'semi-furnished' }),
  mkListing(6, SOCIETIES[4], '402', 2, 21000, 'AVAILABLE', { pets_allowed: 'all pets', furnishing: 'semi-furnished', furn_kitchen_cabinet: true }),
  mkListing(7, SOCIETIES[5], '101', 1, 14500, 'LET', { pets_allowed: 'cats only' }),
  mkListing(8, SOCIETIES[6], '305', 2, 23000, 'AVAILABLE_UNCONFIRMED', { pets_allowed: 'all pets', furnishing: 'fully furnished', furn_gas_stove: true, furn_kitchen_cabinet: true }),
  mkListing(9, SOCIETIES[7], '1802', 3, 42000, 'AVAILABLE', { pets_allowed: 'no', furnishing: 'fully furnished' }),
  mkListing(10, SOCIETIES[8], '601', 2, 19500, 'AVAILABLE', { pets_allowed: 'case-by-case', furnishing: 'unfurnished' }),
];

const customers: Customer[] = [
  { id: 'cus-1', name: 'Riya (demo)', phone: '+91 98765 43210', source: 'phone_call', stage: 'contacted', consent_state: 'otp_confirmed', can_message: true, on_platform: false, created_at: now(), requirements: [] },
  { id: 'cus-2', name: 'Walk-in customer (demo)', phone: '+91 98765 11111', source: 'walk_in', stage: 'new', consent_state: 'none', can_message: false, on_platform: false, created_at: now(), requirements: [] },
  { id: 'cus-3', name: 'Marketplace lead (demo)', phone: '+91 98765 22222', source: 'marketplace', stage: 'visits_planned', consent_state: 'app', can_message: true, on_platform: true, created_at: now(), requirements: [] },
];
const reqs: Requirement[] = [
  { id: 'req-1', txn_type: 'RENT', bhk_min: 2, bhk_max: 2, budget_min: null, budget_max: 25000, must_haves: { furn_gas_stove: true, furn_kitchen_cabinet: true }, house_rule_needs: { pets: 'dog' }, max_station_distance_m: null, occupants: 2, version: 1, summary: '2 BHK for rent; up to ₹25,000/month; must have: gas stove, kitchen cabinet; needs: pets' },
];
customers[0].requirements = [reqs[0]];
const timelines: Record<string, TimelineItem[]> = {
  'cus-1': [
    { id: 't1', kind: 'call_in', summary: 'Called about 2 BHK near Dhokali, has a beagle', at: now(), by: 'You' },
    { id: 't2', kind: 'system', summary: 'Consent confirmed by OTP', at: now(), by: 'You' },
  ],
};

const leads: Lead[] = [
  { id: 'enq-1', summary: '2 BHK on rent, urgent, around Dhokali (3 km), up to ₹25,000/month, pets, gas stove + kitchen cabinet', state: 'open', txn_type: 'RENT', created_at: now(), expires_at: now(), urgency: 'urgent', match_count: 3, my_proposal: null },
  { id: 'enq-2', summary: '3 BHK on rent, around Hiranandani Estate (2 km), up to ₹45,000/month, covered parking', state: 'open', txn_type: 'RENT', created_at: now(), expires_at: now(), urgency: 'normal', match_count: 2, my_proposal: 'sent' },
  { id: 'enq-3', summary: '1 BHK on rent, around Manpada (2 km), up to ₹17,000/month, bachelors', state: 'open', txn_type: 'RENT', created_at: now(), expires_at: now(), urgency: 'normal', match_count: 1, my_proposal: null },
];

const staff: StaffMember[] = [
  { id: 'mem-1', user_id: 'usr-me', name: 'You (principal)', role: 'broker_principal', active: true },
  { id: 'mem-2', user_id: 'usr-imran', name: 'Imran (field staff)', role: 'broker_staff', active: true },
];

function stopFor(l: Listing, i: number, start: Date): VisitStop {
  const s = new Date(start.getTime() + i * 30 * 60000);
  const soc = SOCIETIES.find((x) => x.society_id === l.society_id)!;
  return {
    id: id('stp'), seq: i + 1, listing_id: l.id, society: l.society, building: l.building, unit_no: l.unit_no,
    slot_start: s.toISOString(), slot_end: new Date(s.getTime() + 15 * 60000).toISOString(), location: soc.location,
    navigate_url: `https://www.google.com/maps/dir/?api=1&destination=${soc.location.lat},${soc.location.lng}`,
    assigned_staff_id: 'usr-imran', owner_notice: 'sent', checkin_at: null, outcome: '',
  };
}
const eleven = new Date();
eleven.setHours(11, 0, 0, 0);
const plans: VisitPlan[] = [
  { id: 'vp-1', customer_id: 'cus-1', customer_name: 'Riya (demo)', date: today(), start_time: '11:00', travel_mode: 'two_wheeler', state: 'customer_confirmed', version: 1, total_travel_min: 14, stops: [listings[0], listings[5], listings[7]].map((l, i) => stopFor(l, i, eleven)), key_warnings: [] },
];

const DICTIONARY: AttributeDef[] = [
  ['pets_allowed', 'Pets allowed', '10 House rules (conduct-based only)', 'enum', ['no', 'cats only', 'small dogs', 'all pets', 'case-by-case'], 'hard', 'essential', 'owner'],
  ['nonveg_cooking', 'Non-veg cooking on premises', '10 House rules (conduct-based only)', 'enum', ['allowed', 'not allowed'], 'hard', 'essential', 'owner'],
  ['bachelors_allowed', 'Bachelors / singles', '10 House rules (conduct-based only)', 'enum', ['allowed', 'not allowed'], 'hard', 'essential', 'owner'],
  ['furnishing', 'Furnishing level', '03 Furnishing', 'enum', ['unfurnished', 'semi-furnished', 'fully furnished'], 'hard', 'essential', 'broker'],
  ['car_parking_covered', 'Covered car parking (count)', '05 Parking', 'int', [], 'hard', 'essential', 'broker'],
  ['lift', 'Lift', '06 Building & society amenities', 'bool', [], 'hard', 'essential', 'building'],
  ['furn_gas_stove', 'Gas stove / hob', '03 Furnishing', 'bool', [], 'soft', 'recommended', 'owner'],
  ['furn_kitchen_cabinet', 'Kitchen cabinets (modular)', '03 Furnishing', 'bool', [], 'soft', 'recommended', 'owner'],
  ['piped_gas', 'Piped gas (MGL) connection', '04 Utilities & services', 'bool', [], 'soft', 'recommended', 'owner'],
  ['power_backup', 'Power backup', '04 Utilities & services', 'enum', ['none', 'lift & common areas', 'full'], 'soft', 'recommended', 'building'],
  ['gym', 'Gym', '06 Building & society amenities', 'bool', [], 'soft', 'recommended', 'building'],
  ['water_24x7', '24-hour water', '04 Utilities & services', 'bool', [], 'soft', 'recommended', 'building'],
].map(([key, label, category, type, values, matching, tier, asked_of]) => ({
  key, label, category, scope: 'unit', type, values, unit: '', matching, tier, asked_of,
} as AttributeDef));

function clone<T>(x: T): T {
  return JSON.parse(JSON.stringify(x));
}

function demoMatch(req: Requirement): MatchResult[] {
  return listings
    .filter((l) => l.txn_type === req.txn_type && ['AVAILABLE', 'AVAILABLE_UNCONFIRMED'].includes(l.status))
    .map((l) => {
      const chips: Chip[] = [];
      let excluded = false;
      let score = 100;
      const bhkOk = l.bhk >= req.bhk_min && l.bhk <= req.bhk_max;
      chips.push({ key: 'bhk', label: 'BHK', result: bhkOk ? 'ok' : 'fail', detail: `${l.bhk} BHK` });
      excluded ||= !bhkOk;
      const price = l.asking_rent ?? 0;
      const budgetOk = price <= req.budget_max * 1.1;
      chips.push({ key: 'budget', label: 'Budget', result: budgetOk ? 'ok' : 'fail', detail: `₹${price.toLocaleString('en-IN')}` });
      excluded ||= !budgetOk;
      if (price > req.budget_max) score -= 8;
      if (l.status === 'AVAILABLE_UNCONFIRMED') {
        chips.push({ key: 'status', label: 'Availability', result: 'unknown', detail: 'not yet confirmed by owner' });
        score -= 8;
      } else chips.push({ key: 'status', label: 'Availability', result: 'ok', detail: 'confirmed' });
      for (const k of Object.keys(req.must_haves)) {
        const v = l.attributes?.[k]?.value;
        const label = DICTIONARY.find((d) => d.key === k)?.label ?? k;
        if (v === undefined) {
          chips.push({ key: k, label, result: 'unknown', detail: 'not confirmed' });
          score -= 4;
        } else chips.push({ key: k, label, result: v ? 'ok' : 'fail', detail: '' });
      }
      if (req.house_rule_needs.pets) {
        const rule = l.attributes?.pets_allowed?.value as string | undefined;
        const blocked = rule === 'no' || rule === 'cats only';
        chips.push({ key: 'pets_allowed', label: 'Pets', result: rule === undefined ? 'unknown' : blocked ? 'fail' : 'ok', detail: rule ?? '' });
        excluded ||= blocked;
      }
      return { listing: clone(l), score: excluded ? 0 : Math.max(0, score), excluded, explanation: chips };
    })
    .sort((a, b) => Number(a.excluded) - Number(b.excluded) || b.score - a.score);
}

export function createDemoApi(): Api {
  const tokens: Tokens = { access: 'demo', refresh: 'demo', role: 'broker_principal', org: 'org-demo' };
  let online = false;
  return {
    mode: 'demo',
    async requestOtp() {
      await wait();
      return { dev_code: '123456' };
    },
    async verifyOtp(phone, code) {
      await wait();
      if (code !== '123456') throw new Error('Incorrect OTP. In the demo the code is 123456.');
      return { ...tokens, role: phone.endsWith('0010000') ? 'broker_staff' : 'broker_principal' };
    },
    async me() {
      return { id: 'usr-me', display_name: 'Demo Broker', phone_masked: '+91 ••••• 001', memberships: [{ org_id: 'org-demo', org_name: 'Demo Realty Dhokali', role: 'broker_principal' }], active_role: 'broker_principal', active_org_id: 'org-demo' };
    },
    async switchRole() {
      return tokens;
    },
    async registerOrg() {
      await wait();
      return { tokens };
    },
    async listings(p) {
      await wait(150);
      return clone(listings.filter((l) => (!p?.txn_type || l.txn_type === p.txn_type) && (!p?.status || p.status.split(',').includes(l.status))));
    },
    async listing(lid) {
      await wait(100);
      const l = listings.find((x) => x.id === lid);
      if (!l) throw new Error('Not found');
      return clone(l);
    },
    async createListing(b) {
      await wait();
      const soc = SOCIETIES.find((s) => s.society_id === b.society_id) ?? SOCIETIES[0];
      const w = WINGS[soc.society_id];
      const chk = checkFlat(soc.name, w.wings, w.wings_complete, b.building, b.unit_no, b.floor);
      if (chk.blocking || (chk.issues.length && !b.confirm_layout)) {
        const first = chk.issues.find((i) => i.blocking) ?? chk.issues[0];
        throw new ApiError(chk.blocking ? 422 : 409, first.message, { detail: first.message, layout: chk });
      }
      b = { ...b, building: chk.wing ?? b.building };
      const l = mkListing(++seq, soc, b.unit_no, Number(b.bhk), b.asking_rent ?? 0, 'AVAILABLE_UNCONFIRMED', b.attributes ?? {});
      l.building = b.building || 'Main';
      l.deposit = b.deposit ?? null;
      listings.unshift(l);
      return clone(l);
    },
    async reportStatus(lid, b) {
      await wait();
      const l = listings.find((x) => x.id === lid)!;
      let st = b.state as UnitState;
      // Reopening a let/sold flat needs the owner's YES (STAT-03), unless recorded on the owner's behalf.
      if (st === 'AVAILABLE' && ['LET', 'SOLD', 'OFF_MARKET', 'AVAILABLE_UNCONFIRMED', 'UNKNOWN'].includes(l.status) && !b.on_behalf_of_owner) st = 'AVAILABLE_UNCONFIRMED';
      l.status = st;
      l.status_label = LABEL[st];
      l.last_confirmed_at = now();
      l.stale = false;
      return { state: st, label: LABEL[st] };
    },
    async reconfirm(lid) {
      const l = listings.find((x) => x.id === lid)!;
      l.stale = false;
      l.last_confirmed_at = now();
      return { state: l.status, label: l.status_label };
    },
    async setKeys(lid, b) {
      const l = listings.find((x) => x.id === lid)!;
      l.keys = { holder_type: b.holder_type, holder_user_id: b.holder_user_id ?? null, instructions: b.instructions ?? '', needs_handover: false };
      return {};
    },
    async searchSocieties(q) {
      await wait(120);
      return findSocieties(q);
    },
    async searchFlats(q) {
      await wait(120);
      // Same idea as the server: the last token that looks like a flat number, the rest is the place.
      const tokens = q.trim().split(/[\s,]+/).filter(Boolean);
      let unitNo = '';
      let wing = '';
      if (tokens.length && /\d/.test(tokens[tokens.length - 1]) && /^([a-z]\s*[-/]?\s*)?\d{1,4}[a-z]?$|^(g|ph)-?\d{1,2}$/i.test(tokens[tokens.length - 1])) {
        const u = parseUnitNo(tokens.pop()!);
        unitNo = u.unitNo;
        wing = u.wing;
        if (!wing && tokens.length && /^[a-z]$/i.test(tokens[tokens.length - 1])) wing = tokens.pop()!.toUpperCase();
      }
      const text = tokens.join(' ');
      if (!text && !unitNo) return { results: [], unit_no: '', wing: '' };
      const socs = text ? findSocieties(text) : [];
      const hits = listings
        .filter((l) => !text || socs.some((s) => s.society_id === l.society_id))
        .filter((l) => !unitNo || l.unit_no.toUpperCase().startsWith(unitNo))
        .sort((a, b) => Number(a.unit_no.toUpperCase() !== unitNo) - Number(b.unit_no.toUpperCase() !== unitNo)
          || Number(!!wing && !a.building.toUpperCase().startsWith(wing)) - Number(!!wing && !b.building.toUpperCase().startsWith(wing)));
      return clone({ results: hits.slice(0, 20), unit_no: unitNo, wing });
    },
    async wings(sid) {
      return clone(WINGS[sid] ?? { wings: [], wings_complete: false });
    },
    async checkFlat(sid, p) {
      await wait(80);
      const soc = SOCIETIES.find((s) => s.society_id === sid) ?? SOCIETIES[0];
      const w = WINGS[soc.society_id];
      return checkFlat(soc.name, w.wings, w.wings_complete, p.wing, p.unit_no, p.floor);
    },
    async reportLayout() {
      await wait();
      return { detail: 'Thanks — our team will check the building record, usually within a day.' };
    },
    async localities() {
      return ['Dhokali', 'Manpada', 'Kolshet', 'Majiwada', 'Hiranandani Estate', 'Vasant Vihar'].map((name, i) => ({ id: `loc-${i}`, name, micro_market: 'Thane West', centroid: { lat: 19.23, lng: 72.97 } }));
    },
    async dictionary(p) {
      return DICTIONARY.filter((d) => !p?.tier || p.tier.split(',').includes(d.tier)).filter((d) => !p?.matchable || d.matching !== 'display');
    },
    async customers(q) {
      await wait(150);
      return clone(customers.filter((c) => !q || c.name.toLowerCase().includes(q.toLowerCase()) || c.phone.replace(/\D/g, '').includes(q.replace(/\D/g, '') || '§')));
    },
    async captureCustomer(b) {
      await wait();
      const digits = b.phone.replace(/\D/g, '').slice(-10);
      const existing = customers.find((c) => c.phone.replace(/\D/g, '').endsWith(digits));
      if (existing) return clone(existing);
      const c: Customer = { id: id('cus'), name: b.name || '', phone: `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`, source: b.source, stage: 'new', consent_state: 'none', can_message: false, on_platform: false, created_at: now(), requirements: [] };
      customers.unshift(c);
      timelines[c.id] = [{ id: id('t'), kind: 'system', summary: `Customer added (${b.source.replace('_', ' ')})`, at: now(), by: 'You' }];
      return clone(c);
    },
    async customer(cid) {
      await wait(100);
      return clone(customers.find((c) => c.id === cid)!);
    },
    async timeline(cid) {
      return clone(timelines[cid] ?? []);
    },
    async logInteraction(cid, b) {
      (timelines[cid] ??= []).unshift({ id: id('t'), kind: b.kind, summary: b.summary, at: now(), by: 'You' });
      return {};
    },
    async requestConsent(cid, method) {
      await wait();
      const c = customers.find((x) => x.id === cid)!;
      if (method === 'attested') {
        c.consent_state = 'attested_verbal';
        c.can_message = true;
      }
      (timelines[cid] ??= []).unshift({ id: id('t'), kind: 'system', summary: `Consent requested (${method})`, at: now(), by: 'You' });
      return { sent: method === 'otp' ? 'otp' : 'link', ...(method === 'otp' ? { dev_code: '123456' } : {}) };
    },
    async verifyConsent(cid, code) {
      await wait();
      if (code !== '123456') throw new Error('Incorrect OTP (demo code is 123456)');
      const c = customers.find((x) => x.id === cid)!;
      c.consent_state = 'otp_confirmed';
      c.can_message = true;
      return { consent_state: c.consent_state };
    },
    async addRequirement(cid, b) {
      await wait();
      const r: Requirement = {
        id: id('req'), txn_type: (b.txn_type as never) ?? 'RENT', bhk_min: Number(b.bhk_min), bhk_max: Number(b.bhk_max), budget_min: null,
        budget_max: Number(b.budget_max), must_haves: (b.must_haves as never) ?? {}, house_rule_needs: (b.house_rule_needs as never) ?? {},
        max_station_distance_m: null, occupants: null, version: 1, summary: `${b.bhk_min} BHK for rent; up to ₹${Number(b.budget_max).toLocaleString('en-IN')}/month`,
      };
      reqs.push(r);
      const c = customers.find((x) => x.id === cid)!;
      c.requirements = [r, ...(c.requirements ?? [])];
      return clone(r);
    },
    async match(rid, includeExcluded) {
      await wait(300);
      const all = demoMatch(reqs.find((r) => r.id === rid)!);
      return { considered: all.length, matched: all.filter((m) => !m.excluded).length, results: includeExcluded ? all : all.filter((m) => !m.excluded) };
    },
    async createShortlist(_cid, ids) {
      return { id: id('sl'), items: ids.length };
    },
    async shareShortlist() {
      await wait();
      return {};
    },
    async visitPlans(date) {
      await wait(120);
      return clone(plans.filter((p) => !date || p.date === date));
    },
    async visitPlan(pid) {
      return clone(plans.find((p) => p.id === pid)!);
    },
    async createVisitPlan(b) {
      await wait();
      const start = new Date(`${b.date}T${b.start_time}:00`);
      const c = customers.find((x) => x.id === b.customer_id)!;
      const p: VisitPlan = {
        id: id('vp'), customer_id: c.id, customer_name: c.name, date: b.date, start_time: b.start_time, travel_mode: 'two_wheeler',
        state: 'draft', version: 1, total_travel_min: 6 * b.listing_ids.length,
        stops: b.listing_ids.map((lid, i) => ({ ...stopFor(listings.find((l) => l.id === lid)!, i, start), assigned_staff_id: null, owner_notice: 'not_required' })),
        key_warnings: [],
      };
      plans.unshift(p);
      return clone(p);
    },
    async planAction(pid, action, b) {
      await wait();
      const p = plans.find((x) => x.id === pid)!;
      p.version++;
      if (action === 'share') p.state = p.state === 'draft' ? 'shared' : p.state;
      if (action === 'assign') p.stops.forEach((s) => (s.assigned_staff_id = String(b?.staff_user_id ?? 'usr-imran')));
      if (action === 'notify-owners') {
        const n = p.stops.filter((s) => s.owner_notice === 'not_required').length;
        p.stops.forEach((s) => (s.owner_notice = 'sent'));
        return { notified: n };
      }
      if (action === 'cancel') p.state = 'cancelled';
      if (action === 'add-stop') {
        const l = listings.find((x) => x.id === b?.listing_id);
        if (l && !p.stops.some((s) => s.listing_id === l.id)) {
          const start = new Date(`${p.date}T${p.start_time}:00`);
          p.stops.push({ ...stopFor(l, p.stops.length, start), assigned_staff_id: null, owner_notice: 'not_required' });
          p.total_travel_min = (p.total_travel_min ?? 0) + 6;
        }
      }
      if (action === 'reorder' && Array.isArray(b?.stop_ids)) {
        const order = b!.stop_ids as string[];
        p.stops.sort((a, c) => order.indexOf(a.id) - order.indexOf(c.id)).forEach((s, i) => (s.seq = i + 1));
      }
      return clone(p);
    },
    async removeStop(pid, sid) {
      const p = plans.find((x) => x.id === pid)!;
      p.stops = p.stops.filter((s) => s.id !== sid).map((s, i) => ({ ...s, seq: i + 1 }));
      p.version++;
      return clone(p);
    },
    async sync(_device, mutations) {
      await wait(200);
      const results = mutations.map((m) => {
        const stop = plans.flatMap((p) => p.stops).find((s) => s.id === m.stop_id);
        if (!stop) return { idempotency_key: m.idempotency_key, result: 'conflict' as const, detail: { reason: 'stop_removed_by_broker' } };
        if (m.entity === 'checkin') stop.checkin_at = m.client_ts;
        if (m.entity === 'outcome') stop.outcome = m.outcome ?? '';
        return { idempotency_key: m.idempotency_key, result: 'applied' as const, detail: {} };
      });
      return { results, plans: clone(plans.filter((p) => p.date === today())) };
    },
    async leads() {
      await wait(150);
      return clone(leads);
    },
    async propose(eid) {
      await wait();
      const l = leads.find((x) => x.id === eid)!;
      l.my_proposal = 'sent';
      return {};
    },
    async presence(on) {
      online = on;
      return { online };
    },
    async staff() {
      return clone(staff);
    },
    async inviteStaff(b) {
      const m: StaffMember = { id: id('mem'), user_id: id('usr'), name: b.display_name || b.phone, role: b.role, active: true };
      staff.push(m);
      return clone(m);
    },
  };
}
