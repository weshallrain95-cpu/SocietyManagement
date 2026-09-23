// HTTP implementation of the Api contract against the Django backend.
import type { Api, Tokens } from './types';

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
    const t = tokens.get();
    const headers: Record<string, string> = { Accept: 'application/json' };
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (t?.access) headers.Authorization = `Bearer ${t.access}`;
    let r: Response;
    try {
      r = await fetch(`${root}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
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
    reportStatus: (id, b) => post(`/listings/${id}/status`, b),
    reconfirm: (id) => post(`/listings/${id}/reconfirm`),
    setKeys: (id, b) => call('PUT', `/listings/${id}/keys`, b),

    searchSocieties: async (q) => (await get<{ results: never[] }>(`/societies/search${qs({ q })}`)).results,
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
