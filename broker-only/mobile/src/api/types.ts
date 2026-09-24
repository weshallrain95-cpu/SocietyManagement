// Shapes returned by the Only Broker API (/v1). Kept in step with backend/apps/*/api.py.

export type TxnType = 'RENT' | 'SALE_NEW' | 'SALE_RESALE';
export type Role = 'customer' | 'broker_principal' | 'broker_manager' | 'broker_staff';
export type UnitState = 'UNKNOWN' | 'AVAILABLE' | 'AVAILABLE_UNCONFIRMED' | 'ON_HOLD' | 'LET' | 'SOLD' | 'OFF_MARKET';

export interface Tokens {
  access: string;
  refresh: string;
  role: Role;
  org: string | null;
  new_user?: boolean;
}

export interface Me {
  id: string;
  display_name: string;
  phone_masked: string;
  memberships: { org_id: string; org_name: string; role: Role }[];
  active_role: Role;
  active_org_id: string | null;
}

export interface SocietyCandidate {
  society_id: string;
  name: string;
  locality: string;
  status: 'active' | 'provisional';
  score: number;
  location: { lat: number; lng: number };
}

export interface ResolvedAttr {
  value: unknown;
  source: string;
  disputed: boolean;
}

export interface Listing {
  id: string;
  txn_type: TxnType;
  unit_id: string;
  society: string;
  society_id: string;
  building: string;
  unit_no: string;
  floor: number | null;
  bhk: number;
  asking_rent: number | null;
  asking_price: number | null;
  deposit: number | null;
  available_from: string | null;
  status: UnitState;
  status_label: string;
  last_confirmed_at: string;
  origin: string;
  visibility: string;
  stale: boolean;
  // detail only
  maintenance?: number | null;
  negotiable?: boolean;
  brokerage_terms?: string;
  owner_name?: string;
  owner_phone?: string | null;
  private_notes?: string;
  keys?: { holder_type: string; holder_user_id: string | null; instructions: string | null; needs_handover: boolean } | null;
  attributes?: Record<string, ResolvedAttr>;
}

export interface NewListing {
  society_id: string;
  building?: string;
  unit_no: string;
  floor?: number | null;
  bhk: string;
  property_type?: string;
  txn_type: TxnType;
  asking_rent?: number;
  asking_price?: number;
  deposit?: number;
  available_from?: string;
  owner_name?: string;
  owner_phone?: string;
  attributes?: Record<string, unknown>;
  keys?: { holder_type: string; instructions?: string };
  /** Save despite layout warnings (never overrides a verified layout). */
  confirm_layout?: boolean;
}

export interface BuildingLayout {
  floors_total: number | null;
  lowest_floor: number;
  units_per_floor: number | null;
  skip_floors: number[];
  extra_unit_nos: string[];
  verified: boolean;
  source: string;
}

export interface Wing {
  id: string;
  name: string;
  layout: BuildingLayout;
}

export interface LayoutIssue {
  code: string;
  message: string;
  blocking: boolean;
}

/** Server answer to "does this wing and flat exist?" (same shape inside a 409/422 from createListing). */
export interface FlatCheck {
  wing: string | null;
  building: Wing | null;
  issues: LayoutIssue[];
  suggestions: string[];
  blocking: boolean;
}

export interface AttributeDef {
  key: string;
  label: string;
  category: string;
  scope: 'unit' | 'building' | 'society' | 'listing';
  type: 'bool' | 'enum' | 'multi_enum' | 'int' | 'numeric' | 'money' | 'date' | 'text' | 'ref';
  values: string[];
  unit: string;
  matching: 'hard' | 'soft' | 'display';
  tier: 'essential' | 'recommended' | 'detailed' | 'system';
  asked_of: 'broker' | 'owner' | 'building' | 'nobody';
}

export type ConsentState = 'none' | 'attested_verbal' | 'otp_confirmed' | 'link_confirmed' | 'app' | 'withdrawn';

export interface Requirement {
  id: string;
  txn_type: TxnType;
  bhk_min: number;
  bhk_max: number;
  budget_min: number | null;
  budget_max: number;
  must_haves: Record<string, unknown>;
  house_rule_needs: Record<string, unknown>;
  max_station_distance_m: number | null;
  occupants: number | null;
  version: number;
  summary: string;
}

export interface Customer {
  id: string;
  name: string;
  phone: string;
  source: string;
  stage: string;
  consent_state: ConsentState;
  can_message: boolean;
  on_platform: boolean;
  created_at: string;
  notes?: string;
  requirements?: Requirement[];
}

export interface TimelineItem {
  id: string;
  kind: string;
  summary: string;
  at: string;
  by: string | null;
}

export interface Chip {
  key: string;
  label: string;
  result: 'ok' | 'fail' | 'unknown';
  detail: string;
}

export interface MatchResult {
  listing: Listing;
  score: number;
  excluded: boolean;
  explanation: Chip[];
}

export interface VisitStop {
  id: string;
  seq: number;
  listing_id: string;
  society: string;
  building: string;
  unit_no: string;
  slot_start: string | null;
  slot_end: string | null;
  location: { lat: number; lng: number };
  navigate_url: string;
  assigned_staff_id: string | null;
  owner_notice: string;
  checkin_at: string | null;
  outcome: string;
}

export interface VisitPlan {
  id: string;
  customer_id: string;
  customer_name: string;
  date: string;
  start_time: string;
  travel_mode: string;
  state: string;
  version: number;
  total_travel_min: number | null;
  stops: VisitStop[];
  key_warnings?: { stop_id: string; issue: string }[];
}

export interface Lead {
  id: string;
  summary: string;
  state: string;
  txn_type: TxnType;
  created_at: string;
  expires_at: string;
  urgency: 'normal' | 'urgent';
  match_count: number;
  my_proposal: string | null;
}

export interface StaffMember {
  id: string;
  user_id: string;
  name: string;
  role: Role;
  active: boolean;
}

export interface Locality {
  id: string;
  name: string;
  micro_market: string;
  centroid: { lat: number; lng: number };
}

export interface SyncMutation {
  idempotency_key: string;
  entity: 'checkin' | 'outcome' | 'ack';
  stop_id: string;
  client_ts: string;
  outcome?: string;
  reasons?: string[];
  note?: string;
  lat?: number;
  lng?: number;
}

export interface SyncResult {
  idempotency_key: string;
  result: 'applied' | 'duplicate' | 'conflict';
  detail: Record<string, unknown>;
}

export interface Api {
  mode: 'live' | 'demo';
  requestOtp(phone: string): Promise<{ dev_code?: string }>;
  verifyOtp(phone: string, code: string, displayName?: string): Promise<Tokens>;
  me(): Promise<Me>;
  switchRole(role: 'broker' | 'customer', orgId?: string): Promise<Tokens>;
  registerOrg(body: { name: string; txn_types: TxnType[]; rera_agent_no?: string; office_address?: string }): Promise<{ tokens: Tokens }>;

  listings(params?: { txn_type?: TxnType; status?: string }): Promise<Listing[]>;
  listing(id: string): Promise<Listing>;
  createListing(body: NewListing): Promise<Listing>;
  reportStatus(id: string, body: { state: string; reason?: string; on_behalf_of_owner?: boolean }): Promise<{ state: UnitState; label: string }>;
  reconfirm(id: string): Promise<{ state: UnitState; label: string }>;
  setKeys(id: string, body: { holder_type: string; instructions?: string; holder_user_id?: string }): Promise<unknown>;

  searchSocieties(q: string): Promise<SocietyCandidate[]>;
  wings(societyId: string): Promise<{ wings: Wing[]; wings_complete: boolean }>;
  checkFlat(societyId: string, p: { wing?: string; unit_no: string; floor?: number }): Promise<FlatCheck>;
  reportLayout(buildingId: string, body: { unit_no: string; note?: string }): Promise<{ detail: string }>;
  localities(): Promise<Locality[]>;
  dictionary(params?: { tier?: string; matchable?: boolean; txn?: TxnType }): Promise<AttributeDef[]>;

  customers(q?: string): Promise<Customer[]>;
  captureCustomer(body: { phone: string; name?: string; source: string; notes?: string }): Promise<Customer>;
  customer(id: string): Promise<Customer>;
  timeline(id: string): Promise<TimelineItem[]>;
  logInteraction(id: string, body: { kind: string; summary: string; duration_s?: number }): Promise<unknown>;
  requestConsent(id: string, method: 'otp' | 'link' | 'attested', note?: string): Promise<{ sent: string; dev_code?: string }>;
  verifyConsent(id: string, code: string): Promise<{ consent_state: ConsentState }>;
  addRequirement(customerId: string, body: Record<string, unknown>): Promise<Requirement>;
  match(requirementId: string, includeExcluded?: boolean): Promise<{ considered: number; matched: number; results: MatchResult[] }>;
  createShortlist(customerId: string, listingIds: string[]): Promise<{ id: string; items: number }>;
  shareShortlist(id: string): Promise<unknown>;

  visitPlans(date?: string): Promise<VisitPlan[]>;
  visitPlan(id: string): Promise<VisitPlan>;
  createVisitPlan(body: { customer_id: string; listing_ids: string[]; date: string; start_time: string }): Promise<VisitPlan>;
  planAction(id: string, action: string, body?: Record<string, unknown>): Promise<VisitPlan | { notified: number } | { acknowledged: number }>;
  removeStop(planId: string, stopId: string): Promise<VisitPlan>;
  sync(deviceId: string, mutations: SyncMutation[]): Promise<{ results: SyncResult[]; plans: VisitPlan[] }>;

  leads(): Promise<Lead[]>;
  propose(enquiryId: string, body: { brokerage_terms: string; message?: string }): Promise<unknown>;
  presence(online: boolean): Promise<{ online: boolean }>;

  staff(): Promise<StaffMember[]>;
  inviteStaff(body: { phone: string; display_name?: string; role: 'broker_staff' | 'broker_manager' }): Promise<StaffMember>;
}
