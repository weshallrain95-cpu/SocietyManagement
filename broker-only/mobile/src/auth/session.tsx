import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { createApi, DEFAULT_API_URL, DEMO_FORCED, type Api, type Role, type Tokens } from '@/api';
import { LiveConnection, wsUrl, type LiveEvent } from '@/lib/live';
import { OfflineQueue, newKey } from '@/lib/offlineQueue';
import { kv } from '@/lib/kv';
import { getItem, removeItem, setItem } from '@/lib/storage';

const TOKENS = 'ob.tokens';
const SETTINGS = 'ob.settings';

interface Settings {
  demo: boolean;
  baseUrl: string;
  deviceId: string;
}

interface Session {
  ready: boolean;
  api: Api;
  tokens: Tokens | null;
  role: Role | null;
  isStaff: boolean;
  isOwner: boolean;
  settings: Settings;
  queue: OfflineQueue;
  lastEvent: LiveEvent | null;
  signIn(tokens: Tokens): Promise<void>;
  signOut(): Promise<void>;
  updateSettings(s: Partial<Settings>): Promise<void>;
  dismissEvent(): void;
}

const Ctx = createContext<Session | null>(null);
export const queue = new OfflineQueue(kv);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [tokens, setTokens] = useState<Tokens | null>(null);
  const [settings, setSettings] = useState<Settings>({ demo: DEMO_FORCED, baseUrl: DEFAULT_API_URL, deviceId: newKey() });
  const [lastEvent, setLastEvent] = useState<LiveEvent | null>(null);
  // The API client reads tokens through this store (outside React render); state mirrors it for the UI.
  const [store] = useState(() => {
    let current: Tokens | null = null;
    return {
      get: () => current,
      set: (t: Tokens | null) => {
        current = t;
        setTokens(t);
        if (t) setItem(TOKENS, JSON.stringify(t));
        else removeItem(TOKENS);
      },
    };
  });

  useEffect(() => {
    (async () => {
      const [t, s] = await Promise.all([getItem(TOKENS), kv.getItem(SETTINGS)]);
      if (s) setSettings((prev) => ({ ...prev, ...JSON.parse(s), ...(DEMO_FORCED ? { demo: true } : {}) }));
      else await kv.setItem(SETTINGS, JSON.stringify(settings));
      if (t) store.set(JSON.parse(t));
      setReady(true);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const api = useMemo(
    () => createApi({ demo: settings.demo, baseUrl: settings.baseUrl, tokens: store }),
    [settings.demo, settings.baseUrl, store],
  );

  // Live WebSocket for brokers (not in demo mode).
  useEffect(() => {
    if (!tokens || settings.demo || !tokens.org) return;
    const live = new LiveConnection(wsUrl(settings.baseUrl, tokens.access));
    const off = live.on(setLastEvent);
    live.start();
    return () => {
      off();
      live.stop();
    };
  }, [tokens?.access, tokens?.org, settings.demo, settings.baseUrl]); // eslint-disable-line react-hooks/exhaustive-deps

  // Demo: simulate a new enquiry arriving so the alert can be seen.
  useEffect(() => {
    if (!tokens || !settings.demo) return;
    const t = setTimeout(() => setLastEvent({ event: 'enquiry.new', data: { summary: '2 BHK on rent, urgent, around Dhokali (3 km), up to ₹25,000/month, pets', match_count: 3 } }), 8000);
    return () => clearTimeout(t);
  }, [tokens, settings.demo]);

  const signIn = useCallback(async (t: Tokens) => store.set(t), [store]);
  const signOut = useCallback(async () => store.set(null), [store]);

  const updateSettings = useCallback(
    async (s: Partial<Settings>) => {
      const next = { ...settings, ...s };
      setSettings(next);
      await kv.setItem(SETTINGS, JSON.stringify(next));
    },
    [settings],
  );

  const value: Session = {
    ready, api, tokens, role: tokens?.role ?? null, isStaff: tokens?.role === 'broker_staff', isOwner: tokens?.role === 'owner', settings, queue, lastEvent,
    signIn, signOut, updateSettings, dismissEvent: () => setLastEvent(null),
  };
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSession(): Session {
  const s = useContext(Ctx);
  if (!s) throw new Error('useSession outside SessionProvider');
  return s;
}
