import { checkFlat, checkUnit, parseUnitNo } from '@/lib/layout';
import type { Wing } from '@/api/types';

const wing = (name: string, verified = true): Wing => ({
  id: name, name,
  layout: { floors_total: 20, lowest_floor: 1, units_per_floor: 4, skip_floors: [11], extra_unit_nos: ['PH1'], verified, source: 'survey' },
});
const W = [wing('A Wing'), wing('B Wing')];

test('parses flat numbers like the server', () => {
  expect(parseUnitNo('B-1203')).toEqual({ unitNo: '1203', floor: 12, wing: 'B' });
  expect(parseUnitNo('G-2')).toEqual({ unitNo: 'G2', floor: 0, wing: '' });
});

test('impossible flats', () => {
  expect(checkUnit(W[0], '1204')).toEqual([]);
  expect(checkUnit(W[0], 'PH1')).toEqual([]);
  expect(checkUnit(W[0], '2504')[0]).toMatchObject({ code: 'above_top_floor', blocking: true });
  expect(checkUnit(W[0], '1206')[0].code).toBe('no_such_flat_position');
  expect(checkUnit(W[0], '1103')[0].code).toBe('no_flats_on_floor');
  expect(checkUnit(wing('X', false), '2504')[0].blocking).toBe(false);
});

test('wings: short names, unknown wings, which wing', () => {
  expect(checkFlat('HE', W, true, 'b', '1203').building?.name).toBe('B Wing');
  expect(checkFlat('HE', W, true, undefined, 'A-1203').building?.name).toBe('A Wing');
  expect(checkFlat('HE', W, true, undefined, '1203').issues[0].code).toBe('which_wing');
  const r = checkFlat('HE', W, true, 'Z', '1203');
  expect(r.blocking).toBe(true);
  expect(r.suggestions).toEqual(['A Wing', 'B Wing']);
  expect(checkFlat('HE', W, false, 'Tower 9', '1203').issues).toEqual([]);
});
