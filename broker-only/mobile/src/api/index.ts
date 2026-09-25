import { Platform } from 'react-native';

import { createDemoApi } from './demo';
import { createHttpApi, type TokenStore } from './http';
import type { Api } from './types';

export * from './types';
export { ApiError } from './http';

/** Demo mode runs entirely in the app (online preview); live mode talks to the backend. */
export const DEMO_FORCED = process.env.EXPO_PUBLIC_DEMO === '1';
// The Android emulator reaches the Mac as 10.0.2.2 ("localhost" there is the emulator itself).
export const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_URL ?? (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000');

export function createApi(opts: { demo: boolean; baseUrl: string; tokens: TokenStore }): Api {
  return opts.demo ? createDemoApi() : createHttpApi(opts.baseUrl, opts.tokens);
}
