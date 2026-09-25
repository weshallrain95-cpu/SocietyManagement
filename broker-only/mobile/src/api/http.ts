// HTTP implementation of the Api contract against the Django backend.
import type { Api, ImportSource, Tokens, UploadFile, Wing } from './types';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: unknown,
  ) {
    super(message);
  }
}

export interface TokenStore {
  get(): Tokens | null;
  set(tokens: Tokens | null): void;
  /** Resolves once saved tokens are loaded; requests wait for it (a page reloaded on the web fires queries at once). */
  loaded?: Promise<void>;
}

/** Web pickers give a File; phones give a local uri that React Native's FormData uploads itself. */
function appendFile(f: FormData, field: string, u: UploadFile) {
  if (u.file) f.append(field, u.file, u.name);
  else f.append(field, { uri: u.uri, name: u.name, type: u.type } as unknown as Blob);
}

function importBody(src: ImportSource): FormData | { text: string } {
  if ('text' in src) return { text: src.text };
  const f = new FormData();
  appendFile(f, 'file', src.file);
  return f;
}

function detail(body: unknown, status: number): string {
  if (body && typeof body === 'object') {
    const b = body as Record<string, unknown>;
    if (typeof b.detail === 'string') return b.detail;
    const first = Object.entries(b)[0];
    if (first) {
      const [field, msg] = first;
      const text = Array.isArray(msg) ? String(msg[0]) : String(msg);
      return field === 'non_field_errors' ? text : `${field.replace(/_/g, ' ')}: ${text}`;
    }
  }
  return status >= 500 ? 'Server error. Please try again.' : `Request failed (${status})`;
}

export function createHttpApi(baseUrl: string, tokens: TokenStore): Api {
  const root = baseUrl.replace(/\/+$/, '') + '/v1';
  let refreshing: Promise<boolean> | null = null;

  async function refresh(): Promise<boolean> {
    const t = tokens.get();
    if (!t?.refresh) return false;
    const r = await fetch(`${root}/auth/token/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: t.refresh }),
    });
    if (!r.ok) {
      tokens.set(null);
      return false;
    }
    const body = await r.json();
    tokens.set({ ...t, access: body.access, refresh: body.refresh ?? t.refresh });
    return true;
  }

  async function call<T>(method: string, path: string, body?: unknown, retry = true): Promise<T> {
    if (tokens.loaded) await tokens.loaded;
    const t = tokens.get();
    const headers: Record<string, string> = { Accept: 'application/json' };
    const form = typeof FormData !== 'undefined' && body instanceof FormData;
    if (body !== undefined && !form) headers['Content-Type'] = 'application/json';
    if (t?.access) headers.Authorization = `Bearer ${t.access}`;
    let r: Response;
    try {
      r = await fetch(`${root}${path}`, { method, headers, body: body === undefined ? undefined : form ? (body as FormData) : JSON.stringify(body) });
    } catch {
      throw new ApiError(0, 'No connection to the server. Check your internet and try again.');
    }
    if (r.status === 401 && retry && t?.refresh) {
      refreshing = refreshing ?? refresh().finally(() => (refreshing = null));
      if (await refreshing) return call<T>(method, path, body, false);
    }
    const text = await r.text();
    const parsed = text ? safeJson(text) : null;
    if (!r.ok) throw new ApiError(r.status, detail(parsed, r.status), parsed);
    return parsed as T;
  }

  const get = <T>(p: string) => call<T>('GET', p);
  const post = <T>(p: string, b: unknown = {}) => call<T>('POST', p, b);
  const qs = (o: Record<string, unknown> = {}) => {
    const e = Object.entries(o).filter(([, v]) => v !== undefined && v !== '' && v !== false);
    return e.length ? '?' + e.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&') : '';
  };

  return {
    mode: 'live',
    requestOtp: (phone) => post('/auth/otp/request', { phone }),
    verifyOtp: (phone, code, display_name) => post('/auth/otp/verify', { phone, code, display_name }),
    me: () => get('/me'),
    switchRole: (role, org_id) => post('/auth/switch', { role, org_id }),
    registerOrg: (b) => post('/broker-orgs', b),

    listings: (p) => get(`/listings${qs(p)}`),
    listing: (id) => get(`/listings/${id}`),
    createListing: (b) => post('/listings', b),
    setAvailableNow: (ids, on) => post('/listings/available-now', { listing_ids: ids, available_now: on }),
    reportStatus: (id, b) => post(`/listings/${id}/status`, b),
    reconfirm: (id) => post(`/listings/${id}/reconfirm`),
    setKeys: (id, b) => call('PUT', `/listings/${id}/keys`, b),

    searchSocieties: async (q) => (await get<{ results: never[] }>(`/societies/search${qs({ q })}`)).results,
    searchFlats: (q) => get(`/listings/search${qs({ q })}`),
    browseListings: (p) => get(`/listings/browse${qs({ ...p })}`),
    listingsBySociety: () => get('/listings/by-society'),
    askOwnerBack: (lid, note) => post(`/listings/${lid}/ask-owner-back`, { note }),
    uploadListingMedia: (lid, file) => {
      const f = new FormData();
      appendFile(f, 'file', file);
      return call('POST', `/listings/${lid}/media`, f);
    },
    reviewMedia: (mid, approve) => post(`/owner/media/${mid}/${approve ? 'approve' : 'reject'}`),
    broadcastPreview: (p) => get(`/broadcasts/preview${qs({ ...p })}`),
    sendBroadcast: (b) => post('/broadcasts', b),
    broadcasts: () => get('/broadcasts'),
    importCustomers: (src) => call('POST', '/customers/import', importBody(src)),
    fellowBrokers: (q) => get(`/trade/contacts${qs({ q })}`),
    addFellowBroker: (b) => post('/trade/contacts', b),
    removeFellowBroker: async (cid) => {
      await call('DELETE', `/trade/contacts/${cid}`);
    },
    importFellowBrokers: (src) => call('POST', '/trade/contacts/import', importBody(src)),
    tradePreview: (p) =>
      get(`/trade/blasts/preview${qs({ ...p, listing_ids: p.listing_ids?.join(','), contact_ids: p.contact_ids?.join(','), text: undefined })}`),
    sendTradeBlast: (p) => post('/trade/blasts', p),
    tradeBlasts: () => get('/trade/blasts'),
    tradeBlast: (bid) => get(`/trade/blasts/${bid}`),
    tradeInbox: () => get('/trade/inbox'),
    markTradeRead: () => post('/trade/inbox'),
    replyTrade: (did, answer, message) => post(`/trade/inbox/${did}/reply`, { answer, message }),
    societyStructure: (sid) => get(`/societies/${sid}/structure`),
    myUpdates: () => get('/me/updates'),
    supplyMap: (p) => get(`/map/supply${qs({ bbox: p.bbox.join(','), zoom: p.zoom, txn: p.txn, bhk: p.bhk })}`),
    myEnquiries: () => get('/enquiries'),
    createEnquiry: (b) => post('/enquiries', b),
    enquiry: (id) => get(`/enquiries/${id}`),
    closeEnquiry: (id, state) => post(`/enquiries/${id}/close`, { state }),
    acceptProposal: (id) => post(`/proposals/${id}/accept`),
    markUpdatesRead: () => post('/me/updates'),
    muteBroker: (org_id, muted) => post('/me/updates/mute', { org_id, muted }),
    ownerInvites: () => get('/owner-invites'),
    respondInvite: (iid, action) => post(`/owner-invites/${iid}/${action}`),

    ownerFlats: () => get('/owner/flats'),
    ownerFlat: (fid) => get(`/owner/flats/${fid}`),
    registerFlat: (b) => {
      const f = new FormData();
      f.append('society_id', b.society_id);
      if (b.wing) f.append('wing', b.wing);
      f.append('unit_no', b.unit_no);
      f.append('bhk', b.bhk);
      f.append('declared', b.declared ? 'true' : 'false');
      appendFile(f, 'proof', b.proof);
      return call('POST', '/owner/flats', f);
    },
    setOwnerTerms: (fid, terms, house_rules) => call('PUT', `/owner/flats/${fid}/terms`, { terms, house_rules }),
    uploadMedia: (fid, file) => {
      const f = new FormData();
      appendFile(f, 'file', file);
      return call('POST', `/owner/flats/${fid}/media`, f);
    },
    deleteMedia: async (mid) => {
      await call('DELETE', `/owner/media/${mid}`);
    },
    brokersNearby: (fid) => get(`/owner/flats/${fid}/brokers`),
    inviteBroker: (fid, org_id, allow) => post(`/owner/flats/${fid}/invite`, { org_id, allow }),
    setBrokerAllowed: (fid, oid, allowed, reason) => post(`/owner/flats/${fid}/brokers/${oid}/allowed`, { allowed, reason }),
    reviewBroker: (fid, oid, stars, text) => post(`/owner/flats/${fid}/brokers/${oid}/review`, { stars, text }),
    wings: async (sid) => {
      const s = await get<{ buildings: Wing[]; wings_complete: boolean }>(`/societies/${sid}`);
      return { wings: s.buildings.map(({ id, name, layout }) => ({ id, name, layout })), wings_complete: s.wings_complete };
    },
    checkFlat: (sid, p) => get(`/societies/${sid}/check-flat${qs(p)}`),
    reportLayout: (bid, b) => post(`/buildings/${bid}/layout-report`, b),
    localities: () => get('/localities'),
    dictionary: (p) => get(`/attributes/dictionary${qs({ tier: p?.tier, matchable: p?.matchable ? 1 : undefined, txn: p?.txn })}`),

    customers: (q) => get(`/customers${qs({ q })}`),
    captureCustomer: (b) => post('/customers', b),
    customer: (id) => get(`/customers/${id}`),
    timeline: (id) => get(`/customers/${id}/timeline`),
    logInteraction: (id, b) => post(`/customers/${id}/interactions`, b),
    requestConsent: (id, method, note) => post(`/customers/${id}/consent`, { method, note }),
    verifyConsent: (id, code) => post(`/customers/${id}/consent/verify`, { code }),
    addRequirement: (id, b) => post(`/customers/${id}/requirements`, b),
    match: (id, include_excluded) => post(`/requirements/${id}/match`, { include_excluded: !!include_excluded }),
    createShortlist: (id, listing_ids) => post(`/customers/${id}/shortlists`, { listing_ids }),
    shareShortlist: (id) => post(`/shortlists/${id}/share`),

    visitPlans: (date) => get(`/visit-plans${qs({ date })}`),
    visitPlan: (id) => get(`/visit-plans/${id}`),
    createVisitPlan: (b) => post('/visit-plans', b),
    planAction: (id, action, b) => post(`/visit-plans/${id}/${action}`, b ?? {}),
    removeStop: (planId, stopId) => call('DELETE', `/visit-plans/${planId}/stops/${stopId}`),
    sync: (device_id, mutations) => post('/sync', { device_id, mutations }),

    leads: () => get('/broker/leads'),
    propose: (id, b) => post(`/enquiries/${id}/proposals`, b),
    reportEnquiry: (id, reason) => post(`/enquiries/${id}/report`, { reason }),
    presenceStatus: () => get('/presence'),
    presence: (online) => post('/presence', { online }),

    staff: () => get('/broker-orgs/me/staff'),
    inviteStaff: (b) => post('/broker-orgs/me/staff', b),
  };
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text.slice(0, 200) };
  }
}
