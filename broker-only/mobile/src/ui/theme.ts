import { useColorScheme } from 'react-native';

const light = {
  bg: '#F5F6F3',
  surface: '#FFFFFF',
  surfaceAlt: '#EEF2EF',
  text: '#15201F',
  textMuted: '#5B6866',
  border: '#DCE2DF',
  brand: '#0E3B43',
  brandText: '#FFFFFF',
  accent: '#E08A00',
  ok: '#1E7A46',
  okBg: '#E3F3E9',
  warn: '#9A6200',
  warnBg: '#FFF3DC',
  bad: '#B3261E',
  badBg: '#FBE4E2',
  info: '#1D5C8C',
  infoBg: '#E2EEF8',
};
const dark: typeof light = {
  bg: '#0C1413',
  surface: '#152120',
  surfaceAlt: '#1C2B29',
  text: '#E8EFED',
  textMuted: '#9AAAA7',
  border: '#2A3A38',
  brand: '#5FB3BF',
  brandText: '#0C1413',
  accent: '#F2A93B',
  ok: '#6CCB94',
  okBg: '#173326',
  warn: '#E8B45A',
  warnBg: '#33280F',
  bad: '#F08A83',
  badBg: '#3A1C1A',
  info: '#8CC0E8',
  infoBg: '#172A3A',
};

export type Palette = typeof light;

export function usePalette(): Palette {
  return useColorScheme() === 'dark' ? dark : light;
}

export const space = { xs: 4, sm: 8, md: 12, lg: 16, xl: 24 };
export const radius = { sm: 8, md: 12, lg: 16, pill: 999 };
export const font = { small: 13, body: 15, title: 20, big: 26 };
