// In-app demo backend: the full Api contract over in-memory Thane West sample data.
// Used for the online preview (no server access needed) and for UI development.
// Business rules mirror the backend in simplified form; the backend remains the source of truth.
import type {
  Api, AttributeDef, Chip, Customer, Lead, Listing, MatchResult, Requirement, SocietyCandidate, StaffMember,
  Broadcast, BroadcastInput, CustomerUpdate, FellowBroker, FlatPage, FlatSummary, ImportResult, SocietyStructure, TradeBlast, TradeDelivery, TradeInput, TradePreview, MediaItem, NearbyBroker, OwnerFlat, OwnerInvite, TimelineItem, Tokens, EnquiryDetail, UnitState, VisitPlan, VisitStop, Wing,
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
      ? { wings: ['A', 'B', 'C'].map((w) => ({ id: `bld-${i}-${w}`, name: `${w} Wing`, layout: { ...layout(20, 4, true, [11]), source: 'tmc', extra_unit_nos: w === 'A' ? ['2001A'] : [] } })), wings_complete: true }
      : { wings: [{ id: `bld-${i}-A`, name: 'A Wing', layout: layout(22, 6, false) }], wings_complete: false },
  ]),
);

const LOCALITIES = ['Dhokali', 'Manpada', 'Kolshet', 'Majiwada', 'Hiranandani Estate', 'Vasant Vihar'].map((name, i) => ({ id: `loc-${i}`, name, micro_market: 'Thane West', centroid: { lat: 19.23, lng: 72.97 } }));

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
    available_now: ['AVAILABLE', 'AVAILABLE_UNCONFIRMED', 'ON_HOLD'].includes(state),
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

const OWNERS = ['Mrs Kulkarni', 'Mr Shah', 'Mr Desai', 'Mrs Iyer', 'Mr Rao', 'Mrs Patil', 'Mr Joshi', 'Mrs Menon', 'Mr Bhatia', 'Mrs Gokhale'];
listings.forEach((l, i) => {
  l.owner_name = OWNERS[i % OWNERS.length];
  l.owner_phone = `+91 98190 1${String(2345 + i).padStart(4, '0')}`;
  l.carpet_sqft = [650, 610, 1050, 690, 420, 600, 380, 640, 1120, 600][i % 10];
  l.locality = SOCIETIES.find((x) => x.society_id === l.society_id)?.locality ?? '';
});

const customers: Customer[] = [
  { id: 'cus-1', name: 'Riya (demo)', phone: '+91 98765 43210', source: 'phone_call', stage: 'contacted', consent_state: 'otp_confirmed', can_message: true, on_platform: true, created_at: now(), requirements: [] },
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
  { id: 'mem-1', user_id: 'usr-me', name: 'You (Admin)', role: 'broker_principal', active: true },
  { id: 'mem-3', user_id: 'usr-meena', name: 'Meena (manager)', role: 'broker_manager', permissions: [], active: true },
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

// --- Owner demo data: Mrs Kulkarni owns Hiranandani Estate A Wing 1203 (the flat Demo Realty lists as lst-1). ---
// Photos are drawn placeholders, clearly marked as samples.
function samplePhoto(label: string, hue: number): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480"><rect width="640" height="480" fill="hsl(${hue},35%,78%)"/>`
    + `<rect x="60" y="250" width="520" height="150" fill="hsl(${hue},25%,62%)"/><rect x="380" y="70" width="170" height="130" fill="hsl(200,60%,88%)" stroke="#fff" stroke-width="8"/>`
    + `<text x="40" y="60" font-family="sans-serif" font-size="34" fill="#15201F">${label}</text>`
    + `<text x="40" y="455" font-family="sans-serif" font-size="20" fill="#15201F">Sample photo (demo)</text></svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}
const photo = (id: string, label: string, hue: number): MediaItem => {
  const url = samplePhoto(label, hue);
  return { id, kind: 'photo', state: 'live', uploaded_by: 'Owner', url, thumb_url: url, content_type: 'image/svg+xml', width: 640, height: 480, caption: label, created_at: new Date().toISOString() };
};

export function createDemoApi(): Api {
  const tokens: Tokens = { access: 'demo', refresh: 'demo', role: 'broker_principal', org: 'org-demo' };
  let online = true;
  const enquiries: EnquiryDetail[] = [];
  const ownerMedia: MediaItem[] = [photo('med-1', 'Living room', 28), photo('med-2', 'Kitchen', 140), photo('med-3', 'View from balcony', 205)];
  const ownerFlats: OwnerFlat[] = [{
    id: 'own-1', unit_id: 'unit-1', society: 'Hiranandani Estate', society_id: 'soc-0', locality: 'Hiranandani Estate', building: 'A Wing',
    unit_no: '1203', floor: 12, bhk: 2, claim_status: 'declared', terms: { txn_type: 'RENT', expected_rent: 24000, deposit: 72000 },
    photo_count: 3, video_count: 0, statuses: [{ txn_type: 'RENT', state: 'AVAILABLE', label: 'Available for rent' }],
    brokers: [
      { org_id: 'org-demo', name: 'Demo Realty Dhokali', contact: '+91 98200 00001', rating: 4.6, rating_count: 23, since: '2026-08-02T10:00:00+05:30', owner_appointed: false, allowed: true, asked_back: '' },
      { org_id: 'org-omsai', name: 'Om Sai Estate Agents', contact: '+91 98200 00002', rating: 4.1, rating_count: 9, since: '2026-09-10T10:00:00+05:30', owner_appointed: false, allowed: true, asked_back: '' },
    ],
    invites: [], media: ownerMedia, proof_on_file: true,
  }];
  const nearby: NearbyBroker[] = [
    { org_id: 'org-demo', name: 'Demo Realty Dhokali', rating: 4.6, rating_count: 23, closures: 41, median_response_min: 6, rera_verified: true, serving: true, withdrawn: false },
    { org_id: 'org-shree', name: 'Shree Ganesh Properties', rating: 4.8, rating_count: 31, closures: 57, median_response_min: 4, rera_verified: true, serving: false, withdrawn: false },
    { org_id: 'org-omsai', name: 'Om Sai Estate Agents', rating: 4.1, rating_count: 9, closures: 12, median_response_min: 15, rera_verified: false, serving: true, withdrawn: false },
    { org_id: 'org-thane', name: 'Thane Homes & Rentals', rating: 0, rating_count: 0, closures: 0, median_response_min: null, rera_verified: true, serving: false, withdrawn: false },
  ];
  const invites: OwnerInvite[] = [{
    id: 'inv-1', state: 'pending', society: 'Hiranandani Meadows', locality: 'Pokhran Road', building: 'B Wing', unit_no: '704', bhk: 2,
    txn_type: 'RENT', terms: { txn_type: 'RENT', expected_rent: 32000, deposit: 96000, available_from: indiaDate(10) }, owner_name: 'Mr Deshpande',
    allowed_at: new Date().toISOString(), listing_id: null,
  }];
  // Customer Riya (9876543210) sees updates from her brokers; the demo broker's broadcasts land here too.
  const updates: CustomerUpdate[] = [
    { id: 'upd-0', org_id: 'org-demo', org: 'Demo Realty Dhokali', kind: 'new_flat', text: 'New 3 BHK for rent in Rodas Enclave, Hiranandani Estate — ₹38,000/month. Reply to see it. — Demo Realty Dhokali',
      flat: { society: 'Rodas Enclave', locality: 'Hiranandani Estate', bhk: '3 BHK', txn_type: 'RENT', price: 38000, price_label: '₹38,000/month', available_from: null }, sent_at: new Date(Date.now() - 2 * 3600e3).toISOString(), read: false, muted: false },
    { id: 'upd-1', org_id: 'org-omsai', org: 'Om Sai Estate Agents', kind: 'price_drop', text: 'Good news: rents have come down in Manpada. Ask us for the latest flats. — Om Sai Estate Agents', flat: null, sent_at: new Date(Date.now() - 26 * 3600e3).toISOString(), read: true, muted: false },
  ];
  const sent: Broadcast[] = [];
  const localityOf = (l: Listing) => SOCIETIES.find((x) => x.society_id === l.society_id)?.locality ?? '';
  const where = (l: Listing) => (localityOf(l) && localityOf(l) !== l.society ? `${l.society}, ${localityOf(l)}` : l.society);
  const summaryOf = (l: Listing): FlatSummary => ({
    society: l.society, locality: localityOf(l), bhk: `${l.bhk} BHK`, txn_type: l.txn_type, price: l.asking_rent,
    price_label: `₹${(l.asking_rent ?? 0).toLocaleString('en-IN')}/month`, available_from: l.available_from,
  });
  const picked = (b: BroadcastInput) => (b.listing_ids?.length ? b.listing_ids : b.listing_id ? [b.listing_id] : [])
    .map((x) => listings.find((l) => l.id === x)).filter((l): l is Listing => !!l);
  const bcText = (b: BroadcastInput) => {
    const many = picked(b);
    if (b.kind === 'new_flat' && many.length > 1) {
      return ['New flats with Demo Realty Dhokali:', ...many.map((l) => `• ${l.bhk} BHK for rent in ${where(l)} — ${summaryOf(l).price_label}`), 'Reply to see any of them. — Demo Realty Dhokali'].join('\n');
    }
    const l = many[0];
    if (b.kind === 'new_flat' && l) {
      const soc = SOCIETIES.find((x) => x.society_id === l.society_id)!;
      return `New ${l.bhk} BHK for rent in ${l.society}, ${soc.locality} — ₹${(l.asking_rent ?? 0).toLocaleString('en-IN')}/month. Reply to see it. — Demo Realty Dhokali`;
    }
    if (b.kind === 'price_drop') return `Good news: rents have come down in ${LOCALITIES.find((x) => x.id === b.locality_id)?.name ?? 'your preferred area'}. Ask us for the latest flats. — Demo Realty Dhokali`;
    return '';
  };
  const reach = () => {
    const onApp = customers.filter((c) => c.on_platform).length;
    return { total: customers.length, in_app: onApp, muted: 0, not_on_app: customers.length - onApp };
  };
  // Owner decisions reach the broker's own listing of the same flat (lst-1 is unit-1).
  const syncListingFromOwner = (f: OwnerFlat) => {
    const l = listings.find((x) => x.unit_id === f.unit_id);
    if (!l) return;
    const me = f.brokers.find((b) => b.org_id === 'org-demo');
    l.owner_withdrew = me ? !me.allowed : false;
    l.media = l.owner_withdrew ? [] : clone(f.media ?? []);
    l.my_pending_media = clone((f.pending_media ?? []).filter((m) => m.uploaded_by === 'Demo Realty Dhokali'));
  };
  syncListingFromOwner(ownerFlats[0]);
  const flat = (fid: string) => {
    const f = ownerFlats.find((x) => x.id === fid);
    if (!f) throw new Error('Not found');
    return f;
  };
  // --- Co-broking demo (D17): Demo Realty's own list of fellow brokers, and trade offers from others. ---
  type Fellow = FellowBroker & { lat?: number; lng?: number };
  const fellows: Fellow[] = [
    { id: 'fb-1', name: 'Shree Ganesh Properties', firm: 'Shree Ganesh Properties', phone: '+91 98200 00003', address: 'Near Hiranandani Estate gate', locality: 'Hiranandani Estate', has_location: true, on_platform: true, notes: '', distance_km: null, lat: 19.255, lng: 72.97 },
    { id: 'fb-2', name: 'Om Sai', firm: 'Om Sai Estate Agents', phone: '+91 98200 00002', address: 'Manpada Road', locality: 'Manpada', has_location: true, on_platform: true, notes: '', distance_km: null, lat: 19.236, lng: 72.972 },
    { id: 'fb-3', name: 'Ramesh Patil', firm: 'Patil Properties', phone: '+91 98203 00001', address: 'Patlipada', locality: 'Hiranandani Estate', has_location: true, on_platform: false, notes: 'Strong in Estate rentals', distance_km: null, lat: 19.262, lng: 72.975 },
    { id: 'fb-4', name: 'Sunil', firm: 'Sunil Estate Agency', phone: '+91 98203 00004', address: 'Majiwada', locality: 'Majiwada', has_location: true, on_platform: false, notes: '', distance_km: null, lat: 19.213, lng: 72.983 },
    { id: 'fb-5', name: 'Anil', firm: '', phone: '+91 98203 00003', address: '', locality: null, has_location: false, on_platform: false, notes: '', distance_km: null },
  ];
  const km = (a: { lat: number; lng: number }, b: { lat: number; lng: number }) => {
    const r = (x: number) => (x * Math.PI) / 180;
    const h = Math.sin(r(b.lat - a.lat) / 2) ** 2 + Math.cos(r(a.lat)) * Math.cos(r(b.lat)) * Math.sin(r(b.lng - a.lng) / 2) ** 2;
    return 6371 * 2 * Math.asin(Math.sqrt(h));
  };
  const tradeBlasts: TradeBlast[] = [];
  const tradeInbox: TradeDelivery[] = [
    { id: 'td-1', kind: 'flats', from: 'Shree Ganesh Properties', from_phone: '+91 98200 00003', reply: null, read: false, created_at: new Date(Date.now() - 3600e3).toISOString(),
      text: 'Ready flats available:\n• 2 BHK for rent, Lodha Amara, Kolshet — ₹27,000/month\n• 1 BHK for rent, Dosti Imperia, Manpada — ₹17,500/month\nHave a customer? Call Shree Ganesh Properties +91 98200 00003.',
      items: [
        { society: 'Lodha Amara', locality: 'Kolshet', bhk: '2 BHK', txn_type: 'RENT', price: 27000, price_label: '₹27,000/month', available_from: null },
        { society: 'Dosti Imperia', locality: 'Manpada', bhk: '1 BHK', txn_type: 'RENT', price: 17500, price_label: '₹17,500/month', available_from: null },
      ] },
    { id: 'td-2', kind: 'requirement', from: 'Om Sai Estate Agents', from_phone: '+91 98200 00002', reply: null, read: false, created_at: new Date(Date.now() - 20 * 3600e3).toISOString(),
      text: 'Wanted: 3 BHK for rent in Hiranandani Estate, up to ₹40,000/month, move in by 15 Oct. Have one? Call Om Sai Estate Agents +91 98200 00002.',
      items: [{ txn_type: 'RENT', bhk: '3 BHK', localities: ['Hiranandani Estate'], budget_label: 'up to ₹40,000/month', move_in_by: indiaDate(20) }] },
  ];
  const tradeItems = (p: TradeInput) => {
    if (p.kind === 'flats') {
      const ls = (p.listing_ids ?? []).map((x) => listings.find((l) => l.id === x)).filter((l): l is Listing => !!l);
      if (!ls.length) throw new ApiError(400, 'Pick at least one flat from your inventory');
      const centres = ls.map((l) => SOCIETIES.find((x) => x.society_id === l.society_id)!.location);
      const text = [ls.length > 1 ? 'Ready flats available:' : 'Ready flat available:', ...ls.map((l) => `• ${l.bhk} BHK for rent, ${where(l)} — ${summaryOf(l).price_label}`), 'Have a customer? Call Demo Broker (Demo Realty Dhokali) +91 98200 00001.'].join('\n');
      return { items: ls.map(summaryOf), centres, text };
    }
    const r = reqs.find((x) => x.id === p.requirement_id);
    if (!r) throw new ApiError(400, "Pick one of your customers' requirements");
    const item = { txn_type: r.txn_type, bhk: `${r.bhk_min} BHK`, localities: ['Dhokali'], budget_label: `up to ₹${r.budget_max.toLocaleString('en-IN')}/month`, move_in_by: null };
    return { items: [item], centres: [{ lat: 19.227, lng: 72.978 }], text: `Wanted: ${item.bhk} for rent in Dhokali, ${item.budget_label}. Have one? Call Demo Broker (Demo Realty Dhokali) +91 98200 00001.` };
  };
  const tradePreview = (p: TradeInput): TradePreview => {
    const { items, centres, text } = tradeItems(p);
    const radius = Math.max(0.5, Math.min(p.radius_km ?? 3, 50));
    const chosen = new Set(p.contact_ids ?? []);
    const contacts = fellows.map(({ lat, lng, ...c }) => {
      const d = lat !== undefined && lng !== undefined ? Math.min(...centres.map((x) => km({ lat, lng }, x))) : null;
      const inRadius = d !== null && d <= radius;
      const selected = p.scope === 'all' ? true : p.scope === 'selected' ? chosen.has(c.id) : inRadius;
      return { ...c, distance_km: d === null ? null : Math.round(d * 10) / 10, in_radius: inRadius, selected };
    }).sort((a, b) => (a.distance_km ?? 999) - (b.distance_km ?? 999));
    const sel = contacts.filter((c) => c.selected);
    return {
      text, items, radius_km: radius, contacts,
      reach: { total: contacts.length, selected: sel.length, in_app: sel.filter((c) => c.on_platform).length, whatsapp: sel.filter((c) => !c.on_platform).length, no_location: contacts.filter((c) => c.distance_km === null).length },
    };
  };
  const importPeople = (src: { text?: string; file?: unknown }): { name: string; phone: string }[] => {
    if (!('text' in src) || !src.text) return [{ name: 'Imported contact (demo)', phone: '98765 33333' }, { name: 'Imported contact 2 (demo)', phone: '98765 44444' }];
    return src.text.split('\n').map((line) => {
      const m = line.match(/(\+?\d[\d\s-]{8,}\d)/);
      return m ? { name: line.replace(m[1], '').replace(/[,]/g, ' ').trim(), phone: m[1] } : { name: line.trim(), phone: '' };
    }).filter((r) => r.name || r.phone);
  };
  const structureOf = (sid: string): SocietyStructure => {
    const soc = SOCIETIES.find((x) => x.society_id === sid) ?? SOCIETIES[0];
    const w = WINGS[soc.society_id] ?? { wings: [], wings_complete: false };
    const mine = new Set(listings.filter((l) => l.society_id === soc.society_id).map((l) => `${l.building}|${l.unit_no}`));
    return {
      society: { id: soc.society_id, name: soc.name, locality: soc.locality, wings_complete: w.wings_complete },
      sources: [...new Set(w.wings.map((x) => x.layout.source).filter(Boolean))],
      wings: w.wings.map((wing) => {
        const L = wing.layout;
        const floors: SocietyStructure['wings'][number]['floors'] = [];
        for (let f = L.floors_total ?? 0; f >= L.lowest_floor; f--) {
          const skip = L.skip_floors.includes(f);
          const nos = skip ? [] : Array.from({ length: L.units_per_floor ?? 0 }, (_, i) => `${f}${String(i + 1).padStart(2, '0')}`);
          nos.push(...L.extra_unit_nos.filter((x) => (parseUnitNo(x).floor ?? Math.floor(parseInt(x, 10) / 100)) === f));
          floors.push({ floor: f, label: f === 0 ? 'Ground' : String(f), no_flats: skip, flats: nos.map((no) => ({ no, mine: mine.has(`${wing.name}|${no}`) })) });
        }
        return { id: wing.id, name: wing.name, layout: { ...L, register_complete: L.source === 'tmc' }, flats_total: floors.reduce((n, r) => n + r.flats.length, 0), known: floors.length > 0, floors };
      }),
    };
  };
  // The flat page's extra sections (approved design), from the demo listing's attributes.
  const demoPage = (l: Listing): FlatPage => {
    const soc = SOCIETIES.find((x) => x.society_id === l.society_id)!;
    const wing = WINGS[l.society_id]?.wings.find((w) => w.name === l.building) ?? WINGS[l.society_id]?.wings[0];
    const a = l.attributes ?? {};
    const val = (k: string) => a[k]?.value;
    const cap = (v: unknown) => (typeof v === 'string' ? v[0].toUpperCase() + v.slice(1) : v === true ? 'Yes' : String(v));
    const facts = [
      { label: 'Configuration', value: `${l.bhk} BHK` },
      ...(l.carpet_sqft ? [{ label: 'Carpet area', value: `${l.carpet_sqft} sq ft` }] : []),
      { label: 'Floor', value: `${l.floor}${wing?.layout.floors_total ? ` of ${wing.layout.floors_total}` : ''}` },
      ...(val('furnishing') ? [{ label: 'Furnishing', value: cap(val('furnishing')) }] : []),
      { label: 'Facing', value: 'East' }, { label: 'Bathrooms', value: String(Math.max(1, l.bhk)) },
      { label: 'Covered parking', value: '1' },
      ...(l.available_from ? [{ label: 'Available from', value: new Date(l.available_from).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) }] : []),
    ];
    const rules: FlatPage['house_rules'] = [];
    if (val('pets_allowed')) {
      const v = String(val('pets_allowed'));
      rules.push({ label: 'Pets allowed', value: cap(v), tone: v === 'no' ? 'bad' : v.includes('case') || v.includes('only') ? 'warn' : 'ok' });
    }
    rules.push({ label: 'Non-veg cooking', value: 'Allowed', tone: 'ok' });
    const fits = reqs.filter((r) => r.txn_type === l.txn_type && l.bhk >= r.bhk_min && l.bhk <= r.bhk_max && (l.asking_rent ?? 0) <= r.budget_max * 1.1);
    const custs = fits.map((r) => customers.find((c) => (c.requirements ?? []).some((x) => x.id === r.id))).filter(Boolean) as Customer[];
    return {
      facts,
      house_rules: rules,
      in_flat: ['furn_gas_stove', 'furn_kitchen_cabinet'].filter((k) => val(k) === true).map((k): string => (k === 'furn_gas_stove' ? 'Gas stove' : 'Kitchen cabinets')).concat(['Geyser', 'Fans']),
      society_amenities: val('lift') ? ['Lift', 'Gym', '24-hour water', 'Power backup', 'Security'] : ['24-hour water', 'Security'],
      places: [
        { label: 'Railway station: Thane', value: '4.8 km · 18 min drive' }, { label: 'Auto stand', value: '150 m · 1 min drive' },
        { label: 'School', value: '600 m · 3 min drive' }, { label: 'Hospital', value: '2.1 km · 8 min drive' }, { label: 'Mall: Viviana', value: '5.2 km · 16 min drive' },
      ],
      location: soc.location,
      locality: soc.locality,
      building: { id: wing?.id ?? '', name: l.building, floors_total: wing?.layout.floors_total ?? null, units_per_floor: wing?.layout.units_per_floor ?? null, source: wing?.layout.source ?? '', official_list: wing?.layout.source === 'tmc' },
      fitting_customers: { count: custs.length, customers: custs.slice(0, 3).map((c) => ({ customer_id: c.id, requirement_id: c.requirements?.[0]?.id ?? '', name: c.name })) },
      activity: [
        ...(l.id === 'lst-1' ? [{ at: new Date(Date.now() - 4 * 864e5).toISOString(), text: 'Visit with Riya (demo) (field staff: Imran) · liked' }, { at: new Date(Date.now() - 6 * 864e5).toISOString(), text: 'Shared with Riya (demo) · interested' }] : []),
        { at: l.last_confirmed_at, text: `You: ${l.status_label.toLowerCase()}` },
        { at: new Date(Date.now() - 40 * 864e5).toISOString(), text: 'Added to your flats (manual)' },
      ],
      other_brokers: l.id === 'lst-1' ? 1 : 0,
      owner_on_platform: l.id === 'lst-1',
    };
  };
  const summary = (f: OwnerFlat): OwnerFlat => ({ ...clone(f), photo_count: (f.media ?? []).filter((m) => m.kind === 'photo').length, video_count: (f.media ?? []).filter((m) => m.kind === 'video').length });

  // Same idea as the server's flat search, synchronous so other demo calls can reuse it.
  const findFlats = (q: string) => {
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
    return { results: hits.slice(0, 20), unit_no: unitNo, wing };
  };
  const api: Api = {
    mode: 'demo',
    async requestOtp() {
      await wait();
      return { dev_code: '123456' };
    },
    async verifyOtp(phone, code) {
      await wait();
      if (code !== '123456') throw new Error('Incorrect OTP. In the demo the code is 123456.');
      if (phone.endsWith('0020000')) return { ...tokens, role: 'owner', org: null };
      if (phone.endsWith('6543210')) return { ...tokens, role: 'customer', org: null, new_user: false };
      return { ...tokens, role: phone.endsWith('0010000') ? 'broker_staff' : 'broker_principal' };
    },
    async me() {
      return { id: 'usr-me', display_name: 'Demo Broker', phone_masked: '+91 ••••• 001', memberships: [{ org_id: 'org-demo', org_name: 'Demo Realty Dhokali', role: 'broker_principal', can: ['uploads', 'blasts', 'add_staff'] }], active_role: 'broker_principal', active_org_id: 'org-demo' };
    },
    async switchRole(role) {
      return role === 'owner' || role === 'customer' ? { ...tokens, role, org: null } : tokens;
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
      return clone({ ...l, page: demoPage(l) });
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
      l.available_now = b.available_now ?? true;
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
      if (['LET', 'SOLD', 'OFF_MARKET'].includes(st)) l.available_now = false;
      return { state: st, label: LABEL[st] };
    },
    async setAvailableNow(ids, on) {
      await wait();
      let changed = 0;
      for (const l of listings.filter((x) => ids.includes(x.id))) {
        if (on && !['AVAILABLE', 'AVAILABLE_UNCONFIRMED', 'ON_HOLD'].includes(l.status)) {
          l.status = 'AVAILABLE_UNCONFIRMED';
          l.status_label = LABEL.AVAILABLE_UNCONFIRMED;
        }
        if (!!l.available_now !== on) changed += 1;
        l.available_now = on;
      }
      return { changed };
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
    async browseListings(p) {
      await wait(120);
      const q = (p.q ?? '').trim();
      const digits = q.replace(/\D/g, '');
      let pool = listings.slice();
      if (q) {
        if (digits.length >= 10 && !/[a-z]/i.test(q)) pool = pool.filter((l) => (l.owner_phone ?? '').replace(/\D/g, '').endsWith(digits.slice(-10)));
        else {
          const flatHits = new Set(findFlats(q).results.map((l) => l.id));
          pool = pool.filter((l) => flatHits.has(l.id) || (q.length >= 3 && (l.owner_name ?? '').toLowerCase().includes(q.toLowerCase())));
        }
      }
      const stale = (l: Listing) => l.stale;
      const officeKeys = (l: Listing) => l.keys?.holder_type === 'office';
      const photos = (l: Listing) => (l.media ?? []).filter((m) => m.kind === 'photo').length;
      const all = listings;
      const counts = { total: all.length, available_now: all.filter((l) => l.available_now).length, reconfirm: all.filter((l) => stale(l) && l.available_now).length, new: 3, keys_office: all.filter(officeKeys).length, no_photos: all.filter((l) => !photos(l)).length };
      if (p.list === 'available_now') pool = pool.filter((l) => l.available_now);
      if (p.txn_type) pool = pool.filter((l) => p.txn_type!.split(',').includes(l.txn_type));
      if (p.status) pool = pool.filter((l) => p.status!.split(',').includes(l.status));
      if (p.bhk) {
        const want = p.bhk.split(',').map(Number);
        pool = pool.filter((l) => want.some((b) => (b >= 4 ? l.bhk >= 4 : l.bhk === b)));
      }
      if (p.price_min) pool = pool.filter((l) => (l.asking_rent ?? l.asking_price ?? 0) >= p.price_min!);
      if (p.price_max) pool = pool.filter((l) => (l.asking_rent ?? l.asking_price ?? 0) <= p.price_max!);
      if (p.society_id) pool = pool.filter((l) => l.society_id === p.society_id);
      if (p.building_id) pool = pool.filter((l) => `${l.society_id}|${l.building}` === p.building_id);
      if (p.quick === 'reconfirm') pool = pool.filter((l) => stale(l) && l.available_now);
      if (p.quick === 'keys_office') pool = pool.filter(officeKeys);
      if (p.quick === 'no_photos') pool = pool.filter((l) => !photos(l));
      if (p.quick === 'new') pool = pool.slice(0, 3);
      const price = (l: Listing) => l.asking_rent ?? l.asking_price ?? 0;
      if (p.sort === 'price_low') pool.sort((a, b) => price(a) - price(b));
      if (p.sort === 'price_high') pool.sort((a, b) => price(b) - price(a));
      const offset = p.offset ?? 0;
      const page = pool.slice(offset, offset + (p.limit ?? 50)).map((l) => {
        const ph = (l.media ?? []).filter((m) => m.kind === 'photo');
        return { ...clone(l), photo_count: ph.length, has_video: (l.media ?? []).some((m) => m.kind === 'video'), thumb_url: ph[0]?.thumb_url ?? null, keys_holder: l.keys?.holder_type ?? null };
      });
      return { count: pool.length, counts, results: page };
    },
    async listingsBySociety() {
      await wait(100);
      const out: Record<string, { society_id: string; name: string; count: number; wings: Record<string, number> }> = {};
      for (const l of listings) {
        const g = (out[l.society_id] ??= { society_id: l.society_id, name: l.society, count: 0, wings: {} });
        g.count += 1;
        g.wings[l.building] = (g.wings[l.building] ?? 0) + 1;
      }
      return Object.values(out)
        .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
        .map((g) => ({ ...g, wings: Object.entries(g.wings).map(([name, count]) => ({ building_id: `${g.society_id}|${name}`, name, count })) }));
    },
    async searchFlats(q) {
      await wait(120);
      return clone(findFlats(q));
    },
    async askOwnerBack(lid, note) {
      await wait();
      const l = listings.find((x) => x.id === lid);
      const f = ownerFlats.find((x) => x.unit_id === l?.unit_id);
      const b = f?.brokers.find((x) => x.org_id === 'org-demo');
      if (!b || b.allowed) throw new ApiError(400, 'The owner has not removed your firm from this flat');
      b.asked_back = note;
      return { detail: 'Sent. The owner will decide.' };
    },
    async uploadListingMedia(lid, file) {
      await wait(400);
      const l = listings.find((x) => x.id === lid)!;
      if (l.owner_withdrew) throw new ApiError(400, 'Only a firm currently handling this flat can add photos');
      const kind = file.type.startsWith('video/') ? 'video' : 'photo';
      const m: MediaItem = { id: id('med'), kind, state: 'pending', uploaded_by: 'Demo Realty Dhokali', url: file.uri, thumb_url: file.uri, content_type: file.type, width: null, height: null, caption: '', created_at: now() };
      const f = ownerFlats.find((x) => x.unit_id === l.unit_id);
      if (f) {
        f.pending_media = [...(f.pending_media ?? []), m];
        syncListingFromOwner(f);
      } else {
        l.my_pending_media = [...(l.my_pending_media ?? []), m]; // no owner on the platform: waits until one joins
      }
      return clone(m);
    },
    async reviewMedia(mid, approve) {
      await wait();
      const f = ownerFlats.find((x) => (x.pending_media ?? []).some((m) => m.id === mid))!;
      const m = f.pending_media!.find((x) => x.id === mid)!;
      if (approve) {
        const live = (f.media ?? []).filter((x) => x.kind === m.kind).length;
        if (live >= (m.kind === 'video' ? 1 : 5)) throw new ApiError(400, `This flat already shows ${m.kind === 'video' ? '1 video' : '5 photos'} — remove one first`);
        f.media = [...(f.media ?? []), { ...m, state: 'live' }];
      }
      f.pending_media = f.pending_media!.filter((x) => x.id !== mid);
      syncListingFromOwner(f);
      return summary(f);
    },
    async broadcastPreview(b) {
      await wait(100);
      const many = picked(b);
      return { text: bcText(b), flat: many[0] ? summaryOf(many[0]) : null, flats: many.map(summaryOf), reach: reach(), free_in_pilot: true };
    },
    async sendBroadcast(b) {
      await wait();
      const text = (b.text ?? '').trim() || bcText(b);
      if (!text) throw new ApiError(400, 'Write the message');
      const r = reach();
      const many = picked(b);
      const l = many[0];
      const bc: Broadcast = { id: id('bc'), kind: b.kind, text, listing_id: l?.id ?? null, listing_ids: many.map((x) => x.id), locality: null, recipients_total: r.total, delivered_in_app: r.in_app, not_on_app: r.not_on_app, muted: 0, created_at: now() };
      sent.unshift(bc);
      if (!updates.some((u) => u.org_id === 'org-demo' && u.muted)) {
        updates.unshift({ id: id('upd'), org_id: 'org-demo', org: 'Demo Realty Dhokali', kind: b.kind, text, sent_at: now(), read: false, muted: false,
          flat: l ? summaryOf(l) : null, flats: many.map(summaryOf) });
      }
      const invite = customers.filter((c) => !c.on_platform).map((c) => ({
        customer_id: c.id, name: c.name || 'Customer',
        whatsapp_url: `https://wa.me/${c.phone.replace(/\D/g, '')}?text=${encodeURIComponent(`${text}\n\nGet updates like this from Demo Realty Dhokali on the Only Broker app.`)}`,
      }));
      return clone({ ...bc, invite });
    },
    async importCustomers(src) {
      await wait();
      const rows = importPeople(src as { text?: string });
      const out: ImportResult = { added: 0, already_in_book: 0, skipped: [], skipped_count: 0 };
      rows.forEach((r, i) => {
        const digits = r.phone.replace(/\D/g, '').slice(-10);
        if (digits.length !== 10) {
          out.skipped.push({ row: i + 1, reason: 'No valid mobile number', text: r.name.slice(0, 60) });
          return;
        }
        if (customers.some((c) => c.phone.replace(/\D/g, '').endsWith(digits))) {
          out.already_in_book! += 1;
          return;
        }
        customers.push({ id: id('cus'), name: r.name, phone: `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`, source: 'import', stage: 'new', consent_state: 'none', can_message: false, on_platform: false, created_at: now(), requirements: [] });
        out.added += 1;
      });
      out.skipped_count = out.skipped.length;
      return out;
    },
    async fellowBrokers(q) {
      await wait(100);
      const n = (q ?? '').toLowerCase();
      return clone(fellows.filter((c) => !n || `${c.name} ${c.firm} ${c.phone} ${c.locality ?? ''}`.toLowerCase().includes(n)).map(({ lat: _a, lng: _b, ...c }) => c));
    },
    async addFellowBroker(b) {
      await wait();
      const digits = b.phone.replace(/\D/g, '').slice(-10);
      if (digits.length !== 10) throw new ApiError(400, 'Enter a valid mobile number');
      const loc = LOCALITIES.find((l) => `${b.area ?? ''} ${b.address ?? ''}`.toLowerCase().includes(l.name.toLowerCase()));
      const c: Fellow = { id: id('fb'), name: b.name, firm: b.firm ?? '', phone: `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`, address: b.address ?? b.area ?? '', locality: loc?.name ?? null,
        has_location: !!loc, on_platform: false, notes: b.notes ?? '', distance_km: null, ...(loc ? { lat: 19.23, lng: 72.975 } : {}) };
      fellows.push(c);
      const { lat: _a, lng: _b, ...out } = c;
      return clone(out);
    },
    async removeFellowBroker(fid) {
      const i = fellows.findIndex((c) => c.id === fid);
      if (i >= 0) fellows.splice(i, 1);
    },
    async importFellowBrokers(src) {
      await wait();
      const rows = importPeople(src as { text?: string });
      const out: ImportResult = { added: 0, updated: 0, skipped: [], skipped_count: 0 };
      rows.forEach((r, i) => {
        const digits = r.phone.replace(/\D/g, '').slice(-10);
        if (digits.length !== 10 || !r.name) {
          out.skipped.push({ row: i + 1, reason: 'Enter a valid mobile number', text: r.name.slice(0, 60) });
          return;
        }
        if (fellows.some((c) => c.phone.replace(/\D/g, '').endsWith(digits))) {
          out.updated! += 1;
          return;
        }
        fellows.push({ id: id('fb'), name: r.name, firm: '', phone: `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`, address: '', locality: null, has_location: false, on_platform: false, notes: '', distance_km: null });
        out.added += 1;
      });
      out.skipped_count = out.skipped.length;
      return out;
    },
    async tradePreview(p) {
      await wait(120);
      return clone(tradePreview(p));
    },
    async sendTradeBlast(p) {
      await wait();
      const pv = tradePreview(p);
      const text = (p.text ?? '').trim() || pv.text;
      const sel = pv.contacts.filter((c) => c.selected);
      if (!sel.length) throw new ApiError(400, 'Nobody selected. Widen the distance, choose everyone, or tick names.');
      const b: TradeBlast = { id: id('tb'), kind: p.kind, text, items: pv.items, recipients_total: sel.length, delivered_in_app: sel.filter((c) => c.on_platform).length,
        via_whatsapp: sel.filter((c) => !c.on_platform).length, replies_count: 0, audience: { scope: p.scope, radius_km: pv.radius_km }, created_at: now(), replies: [] };
      tradeBlasts.unshift(b);
      // A fellow broker on the platform answers after a moment (demo).
      const first = sel.find((c) => c.on_platform);
      if (first) setTimeout(() => { b.replies!.push({ from: first.firm || first.name, phone: first.phone, message: p.kind === 'flats' ? 'I have a family of 3 looking, can visit Sunday' : 'I have one in Rodas Enclave', at: now() }); b.replies_count = b.replies!.length; }, 4000);
      const whatsapp = sel.filter((c) => !c.on_platform).map((c) => ({ contact_id: c.id, name: c.name, firm: c.firm, whatsapp_url: `https://wa.me/${c.phone.replace(/\D/g, '')}?text=${encodeURIComponent(text)}` }));
      return clone({ ...b, whatsapp });
    },
    async tradeBlasts() {
      return clone(tradeBlasts);
    },
    async tradeBlast(bid) {
      const b = tradeBlasts.find((x) => x.id === bid);
      if (!b) throw new ApiError(404, 'Not found');
      return clone(b);
    },
    async tradeInbox() {
      await wait(100);
      return clone(tradeInbox);
    },
    async markTradeRead() {
      tradeInbox.forEach((d) => (d.read = true));
      return {};
    },
    async replyTrade(did, answer) {
      await wait();
      const d = tradeInbox.find((x) => x.id === did);
      if (!d) throw new ApiError(404, 'Not found');
      d.reply = answer;
      d.read = true;
      return clone(d);
    },
    async societyStructure(sid) {
      await wait(120);
      return clone(structureOf(sid));
    },
    async broadcasts() {
      return clone(sent);
    },
    async supplyMap(p) {
      await wait(120);
      const inBox = (lat: number, lng: number) => lng >= p.bbox[0] && lat >= p.bbox[1] && lng <= p.bbox[2] && lat <= p.bbox[3];
      const clusters = SOCIETIES.filter((s) => inBox(s.location.lat, s.location.lng)).map((s, i) => ({
        h3: `demo-${i}`, lat: s.location.lat, lng: s.location.lng, units: 2 + (i % 4), brokers_serving: 1 + (i % 3),
        price_band: p.txn === 'RENT' ? { p25: 20000 + i * 1000, p50: 24000 + i * 1000, p75: 30000 + i * 1000 } : null,
      }));
      return { clusters, brokers_online: [{ id: 'org-demo', name: 'Demo Realty Dhokali', rating: 4.6, location: null }] };
    },
    async myEnquiries() {
      await wait();
      return clone(enquiries.map(({ proposals, ...e }) => ({ ...e, proposals: proposals.length })));
    },
    async createEnquiry(b) {
      await wait();
      if (enquiries.filter((e) => e.state === 'open' || e.state === 'in_progress').length >= 3) throw new ApiError(400, 'You can have at most 3 open enquiries.');
      const bhkText = b.bhk_min === b.bhk_max ? `${b.bhk_min} BHK` : `${b.bhk_min}–${b.bhk_max} BHK`;
      const e: EnquiryDetail = {
        id: id('enq'), state: 'open', txn_type: b.txn_type, created_at: now(), expires_at: now(), urgency: b.urgency, radius_m: b.radius_m, area_label: b.area_label, recipients: 4,
        summary: `${bhkText} ${b.txn_type === 'RENT' ? 'on rent' : 'to buy'}${b.urgency === 'urgent' ? ', urgent' : ''}, around ${b.area_label} (${b.radius_m / 1000} km), up to ₹${b.budget_max.toLocaleString('en-IN')}`,
        proposals: [{
          id: id('prp'), state: 'sent', brokerage_terms: b.txn_type === 'RENT' ? '1 month rent' : '1% of sale value', message: 'I have flats that fit. Can show them this weekend.',
          match_count: 3, earliest_slot: null, response_s: 240, promoted: false, created_at: now(),
          broker: { id: 'org-demo', name: 'Demo Realty Dhokali', rera_registered: true, rating_bayes: 4.6, rating_count: 18, median_response_s: 300, closures: 42, languages: ['en', 'mr', 'hi'] },
        }],
      };
      enquiries.unshift(e);
      return clone({ ...e, proposals: e.proposals.length });
    },
    async enquiry(eid) {
      await wait();
      return clone(enquiries.find((e) => e.id === eid)!);
    },
    async closeEnquiry(eid, state) {
      await wait();
      const e = enquiries.find((x) => x.id === eid)!;
      e.state = state;
      return clone({ ...e, proposals: e.proposals.length });
    },
    async acceptProposal(pid) {
      await wait();
      const e = enquiries.find((x) => x.proposals.some((p) => p.id === pid))!;
      if (e.proposals.filter((p) => p.state === 'accepted').length >= 3) throw new ApiError(400, 'You can accept at most 3 brokers.');
      const p = e.proposals.find((x) => x.id === pid)!;
      p.state = 'accepted';
      e.state = 'in_progress';
      return clone(p);
    },
    async myUpdates() {
      await wait(100);
      return clone(updates);
    },
    async markUpdatesRead() {
      updates.forEach((u) => (u.read = true));
      return {};
    },
    async muteBroker(orgId, muted) {
      updates.filter((u) => u.org_id === orgId).forEach((u) => (u.muted = muted));
      return { updated: 1 };
    },
    async ownerInvites() {
      await wait(120);
      return clone(invites.filter((i) => i.state === 'pending'));
    },
    async respondInvite(iid, action) {
      await wait();
      const inv = invites.find((i) => i.id === iid)!;
      if (inv.state !== 'pending') throw new ApiError(400, 'This invitation is no longer open');
      if (action === 'decline') {
        inv.state = 'declined';
        return clone(inv);
      }
      const soc = SOCIETIES.find((x) => x.name === inv.society) ?? SOCIETIES[0];
      const l = mkListing(++seq, soc, inv.unit_no, inv.bhk, inv.terms.expected_rent ?? 0, 'AVAILABLE_UNCONFIRMED', {});
      Object.assign(l, { building: inv.building, origin: 'owner_invite', owner_appointed: true, owner_name: inv.owner_name, deposit: inv.terms.deposit ?? null });
      listings.unshift(l);
      inv.state = 'accepted';
      inv.listing_id = l.id;
      return clone({ ...inv, listing_id: l.id });
    },

    async ownerFlats() {
      await wait(120);
      return ownerFlats.map(summary);
    },
    async ownerFlat(fid) {
      await wait(80);
      return summary(flat(fid));
    },
    async registerFlat(b) {
      await wait();
      if (!b.declared) throw new ApiError(400, 'Please confirm that you own this flat');
      const soc = SOCIETIES.find((x) => x.society_id === b.society_id) ?? SOCIETIES[0];
      const w = WINGS[soc.society_id];
      const chk = checkFlat(soc.name, w.wings, w.wings_complete, b.wing, b.unit_no);
      if (chk.blocking) throw new ApiError(400, chk.issues.find((i) => i.blocking)!.message);
      const f: OwnerFlat = {
        id: id('own'), unit_id: id('unit'), society: soc.name, society_id: soc.society_id, locality: soc.locality, building: chk.wing ?? 'Main',
        unit_no: parseUnitNo(b.unit_no).unitNo, floor: parseUnitNo(b.unit_no).floor, bhk: Number(b.bhk), claim_status: 'declared', terms: {},
        photo_count: 0, video_count: 0, statuses: [], brokers: [], invites: [], media: [], proof_on_file: true,
      };
      ownerFlats.unshift(f);
      return summary(f);
    },
    async setOwnerTerms(fid, terms) {
      await wait();
      const f = flat(fid);
      f.terms = { ...terms };
      return summary(f);
    },
    async uploadMedia(fid, file) {
      await wait(400);
      const f = flat(fid);
      const kind = file.type.startsWith('video/') ? 'video' : 'photo';
      const m: MediaItem = { id: id('med'), kind, state: 'live', uploaded_by: 'Owner', url: file.uri, thumb_url: file.uri, content_type: file.type, width: null, height: null, caption: '', created_at: now() };
      f.media = [...(f.media ?? []), m];
      syncListingFromOwner(f);
      return clone(m);
    },
    async deleteMedia(mid) {
      for (const f of ownerFlats) {
        f.media = (f.media ?? []).filter((m) => m.id !== mid);
        syncListingFromOwner(f);
      }
    },
    async brokersNearby(fid) {
      await wait(150);
      const f = flat(fid);
      return clone(nearby.map((n) => {
        const b = f.brokers.find((x) => x.org_id === n.org_id);
        return { ...n, serving: !!b?.allowed, withdrawn: !!b && !b.allowed };
      }));
    },
    async inviteBroker(fid, orgId, allow) {
      await wait();
      if (!allow) throw new ApiError(400, 'Tick “Allow this broker to handle my property” first');
      const f = flat(fid);
      const n = nearby.find((x) => x.org_id === orgId)!;
      const existing = f.brokers.find((b) => b.org_id === orgId);
      if (existing) existing.allowed = true;
      f.invites = [...(f.invites ?? []), { id: id('inv'), org_id: orgId, name: n.name, state: 'pending', sent_at: now() }];
      syncListingFromOwner(f);
      return { id: id('inv'), state: 'pending', allowed_at: now() };
    },
    async setBrokerAllowed(fid, orgId, allowed) {
      await wait();
      const f = flat(fid);
      const b = f.brokers.find((x) => x.org_id === orgId);
      if (b) {
        b.allowed = allowed;
        if (allowed) b.asked_back = '';
      }
      syncListingFromOwner(f);
      return summary(f);
    },
    async reviewBroker(_fid, _orgId, stars) {
      await wait();
      if (stars < 1 || stars > 5) throw new ApiError(400, 'Stars must be 1 to 5');
      return { id: id('rev'), stars };
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
      return clone(LOCALITIES);
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
    async reportEnquiry() {
      await wait();
      return { reported: true };
    },
    async propose(eid) {
      await wait();
      const l = leads.find((x) => x.id === eid)!;
      l.my_proposal = 'sent';
      return {};
    },
    async presenceStatus() {
      return { online };
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
    async removeStaff(mid) {
      const m = staff.find((x) => x.id === mid);
      if (m) m.active = false;
      return {};
    },
    async setTeamPermissions(mid, permissions) {
      const m = staff.find((x) => x.id === mid)!;
      m.permissions = permissions;
      return clone(m);
    },
  };
  return api;
}
