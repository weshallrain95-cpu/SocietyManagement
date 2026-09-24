import type { Chip, ConsentState, UnitState } from '@/api/types';

export function inr(n: number | null | undefined, perMonth = false): string {
  if (n === null || n === undefined) return '—';
  let s: string;
  if (n >= 10_000_000) s = `₹${(n / 10_000_000).toFixed(2).replace(/\.?0+$/, '')} Cr`;
  else if (n >= 100_000) s = `₹${(n / 100_000).toFixed(2).replace(/\.?0+$/, '')} L`;
  else s = `₹${n.toLocaleString('en-IN')}`;
  return perMonth ? `${s}/mo` : s;
}

export function bhk(n: number): string {
  return n === 0.5 ? '1 RK' : `${n % 1 ? n.toFixed(1) : n} BHK`;
}

/** The business runs on India time whatever the device's timezone (travelling phones, test browsers). */
export const TZ = 'Asia/Kolkata';

export function time(iso: string | null | undefined): string {
  if (!iso) return '';
  return new Date(iso).toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', timeZone: TZ });
}

/** YYYY-MM-DD for a day in India time; offsetDays=1 is tomorrow. */
export function indiaDate(offsetDays = 0, now: Date = new Date()): string {
  const d = new Date(now.getTime() + offsetDays * 86_400_000);
  return new Intl.DateTimeFormat('en-CA', { timeZone: TZ, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d);
}

export function dayLabel(isoDate: string, now: Date = new Date()): string {
  if (isoDate === indiaDate(0, now)) return 'Today';
  if (isoDate === indiaDate(1, now)) return 'Tomorrow';
  return new Date(`${isoDate}T12:00:00+05:30`).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', timeZone: TZ });
}

export function ago(iso: string): string {
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  return `${Math.floor(s / 86400)} d ago`;
}

export function statusTone(s: UnitState): 'ok' | 'warn' | 'bad' | 'info' {
  if (s === 'AVAILABLE') return 'ok';
  if (s === 'AVAILABLE_UNCONFIRMED' || s === 'ON_HOLD') return 'warn';
  if (s === 'UNKNOWN') return 'info';
  return 'bad';
}

export function chipIcon(c: Chip): string {
  return c.result === 'ok' ? '✔' : c.result === 'fail' ? '✖' : '≈';
}

export const CONSENT_LABEL: Record<ConsentState, string> = {
  none: 'No consent yet',
  attested_verbal: 'Verbal consent (you attested)',
  otp_confirmed: 'Consent confirmed by OTP',
  link_confirmed: 'Consent confirmed by link',
  app: 'On the app',
  withdrawn: 'Consent withdrawn',
};

/** Accepts "98765 43210", "+91-98765-43210", "098765 43210"; returns 10 digits or null. */
export function indianMobile(raw: string): string | null {
  let d = raw.replace(/\D/g, '');
  if (d.length === 12 && d.startsWith('91')) d = d.slice(2);
  if (d.length === 11 && d.startsWith('0')) d = d.slice(1);
  return /^[6-9]\d{9}$/.test(d) ? d : null;
}

export const OUTCOMES = [
  { value: 'liked', label: 'Liked' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'second_visit', label: 'Wants 2nd visit' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'already_let', label: 'Already let' },
  { value: 'not_accessible', label: 'No access' },
  { value: 'no_show', label: 'Customer no-show' },
] as const;

/** "+919876543210" -> "+91 98765 43210" (other formats pass through). */
export function phone(e164: string | null | undefined): string {
  if (!e164) return '';
  const m = /^\+91(\d{5})(\d{5})$/.exec(e164.replace(/\s/g, ''));
  return m ? `+91 ${m[1]} ${m[2]}` : e164;
}

/** Whole days since an ISO time (0 for today). */
export function daysSince(iso: string): number {
  return Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 864e5));
}
