import { bhk, dayLabel, indiaDate, indianMobile, inr, phone, time } from '@/lib/format';

test('Indian money formats', () => {
  expect(inr(24000, true)).toBe('₹24,000/mo');
  expect(inr(8500000)).toBe('₹85 L');
  expect(inr(12500000)).toBe('₹1.25 Cr');
  expect(inr(null)).toBe('—');
});

test('BHK labels', () => {
  expect(bhk(0.5)).toBe('1 RK');
  expect(bhk(2)).toBe('2 BHK');
  expect(bhk(2.5)).toBe('2.5 BHK');
});

test.each<[string, string | null]>([
  ['98765 43210', '9876543210'],
  ['+91-98765-43210', '9876543210'],
  ['098765 43210', '9876543210'],
  ['12345 67890', null],
  ['98765', null],
])('mobile %s', (raw, want) => expect(indianMobile(raw)).toBe(want));

test('times always show in India time, whatever the device timezone', () => {
  // 11:00 IST == 05:30 UTC; the test runner's own timezone must not matter.
  expect(time('2026-10-03T05:30:00Z').replace(/\s/g, ' ').toLowerCase()).toBe('11:00 am');
});

test("'today' is the India date even just after midnight IST", () => {
  const justAfterMidnightIST = new Date('2026-09-23T20:44:00Z'); // 02:14 IST on the 24th
  expect(indiaDate(0, justAfterMidnightIST)).toBe('2026-09-24');
  expect(indiaDate(1, justAfterMidnightIST)).toBe('2026-09-25');
  expect(dayLabel('2026-09-24', justAfterMidnightIST)).toBe('Today');
  expect(dayLabel('2026-09-25', justAfterMidnightIST)).toBe('Tomorrow');
});

test('phone display', () => {
  expect(phone('+919876577777')).toBe('+91 98765 77777');
  expect(phone('+91 98765 ••••')).toBe('+91 98765 ••••');
});
