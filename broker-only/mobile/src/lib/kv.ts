// Key-value storage that never throws: AsyncStorage when available, memory otherwise.
// (Sandboxed web views and private browsing can refuse storage; the app must still work.)
import AsyncStorage from '@react-native-async-storage/async-storage';

import type { KV } from './offlineQueue';

const memory = new Map<string, string>();

export const kv: KV = {
  async getItem(key) {
    try {
      const v = await AsyncStorage.getItem(key);
      return v ?? memory.get(key) ?? null;
    } catch {
      return memory.get(key) ?? null;
    }
  },
  async setItem(key, value) {
    memory.set(key, value);
    try {
      await AsyncStorage.setItem(key, value);
    } catch {
      /* memory copy is enough for this session */
    }
  },
};
