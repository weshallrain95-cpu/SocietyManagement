// Flat-number checks against a wing's layout (MD-13). The server is the source of truth
// (backend/apps/masterdata/layout.py); this port powers demo mode with the same messages.
import type { FlatCheck, LayoutIssue, Wing } from '@/api/types';

export interface ParsedUnit {
  unitNo: string;
  floor: number | null;
  wing: string;
}

export function parseUnitNo(raw: string): ParsedUnit {
  let s = raw.trim().toLowerCase().replace(/\b(flat|flt|unit|no|apt)\b\.?/g, ' ');
  let wing = '';
  const wm = s.match(/^\s*([a-z])\s*(?:wing)?\s*[-/ ]\s*(\d{2,4})\b/) ?? s.match(/^\s*([a-z])(\d{3,4})\b/);
  if (wm) {
    wing = wm[1].toUpperCase();
    s = wm[2];
  }
  const unitNo = s.replace(/[^a-z0-9]/g, '').toUpperCase() || '?';
  let floor: number | null = null;
  if (/^G\d+$/.test(unitNo)) floor = 0;
  else if (/^\d{3,}$/.test(unitNo)) floor = Number(unitNo.slice(0, -2));
  return { unitNo, floor, wing };
}

const wingKey = (s: string) => s.toUpperCase().replace(/\b(WING|BLOCK|TOWER|BUILDING|BLDG)\b/g, '').replace(/[^A-Z0-9]/g, '') || 'MAIN';
const floorWord = (n: number) => (n === 0 ? 'ground floor' : `floor ${n}`);

export function checkUnit(w: Wing, raw: string, floor?: number | null): LayoutIssue[] {
  const L = w.layout;
  const p = parseUnitNo(raw);
  if (L.extra_unit_nos.some((x) => parseUnitNo(x).unitNo === p.unitNo)) return [];
  const hard = L.verified;
  const out: LayoutIssue[] = [];
  const fl = floor ?? p.floor;
  if (floor != null && p.floor != null && floor !== p.floor)
    out.push({ code: 'floor_mismatch', message: `Flat ${p.unitNo} is normally on ${floorWord(p.floor)}, but ${floorWord(floor)} was entered.`, blocking: false });
  if (fl != null) {
    if (L.floors_total != null && fl > L.floors_total)
      out.push({ code: 'above_top_floor', message: `${w.name} has ${L.floors_total} floors, so flat ${p.unitNo} (${floorWord(fl)}) cannot exist.`, blocking: hard });
    else if (fl >= 0 && fl < L.lowest_floor)
      out.push({ code: 'below_lowest_floor', message: `Flats in ${w.name} start from ${floorWord(L.lowest_floor)}.`, blocking: hard });
    else if (L.skip_floors.includes(fl))
      out.push({ code: 'no_flats_on_floor', message: `${w.name} has no flats on ${floorWord(fl)} (refuge or podium floor).`, blocking: hard });
  }
  if (L.units_per_floor && /^\d{3,}$/.test(p.unitNo)) {
    const pos = Number(p.unitNo.slice(-2));
    if (pos === 0 || pos > L.units_per_floor)
      out.push({
        code: 'no_such_flat_position',
        message: `${w.name} has ${L.units_per_floor} flats per floor (…01 to …${String(L.units_per_floor).padStart(2, '0')}), so flat ${p.unitNo} cannot exist.`,
        blocking: hard,
      });
  }
  return out;
}

export function checkFlat(societyName: string, wings: Wing[], complete: boolean, wing: string | undefined, raw: string, floor?: number | null): FlatCheck {
  const name = (wing ?? '').trim() || parseUnitNo(raw).wing;
  const result = (b: Wing | null, issues: LayoutIssue[], suggestions: string[] = []): FlatCheck => {
    const all = b ? [...issues, ...checkUnit(b, raw, floor)] : issues;
    return { wing: b?.name ?? (name || null), building: b, issues: all, suggestions, blocking: all.some((i) => i.blocking) };
  };
  if (!name) {
    if (wings.length === 1) return result(wings[0], []);
    if (wings.length > 1) return result(null, [{ code: 'which_wing', message: `${societyName} has ${wings.length} wings. Which one?`, blocking: true }], wings.map((w) => w.name));
    return result(null, []);
  }
  const key = wingKey(name);
  const exact = wings.find((w) => wingKey(w.name) === key);
  if (exact) return result(exact, []);
  const short = wings.filter((w) => (key.length <= 2 && wingKey(w.name).endsWith(key)) || (wingKey(w.name).length <= 2 && key.endsWith(wingKey(w.name))));
  if (short.length === 1) return result(short[0], []);
  if (complete)
    return result(null, [{ code: 'unknown_wing', message: `${societyName} has no wing “${name}”. Wings: ${wings.map((w) => w.name).join(', ')}.`, blocking: true }], wings.map((w) => w.name));
  return result(null, []);
}
