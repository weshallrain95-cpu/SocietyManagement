// Field staff: today's plans cached on the device, actions queued, auto-sync when back online.
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { useCallback, useEffect, useState } from 'react';

import type { SyncMutation, VisitPlan } from '@/api';
import { useSession } from '@/auth/session';
import { indiaDate } from '@/lib/format';

const CACHE = 'ob.staff.day.v1';

/** Apply queued (not yet synced) actions on top of the cached server state, so the UI shows them at once. */
export function overlay(plans: VisitPlan[], pending: SyncMutation[]): VisitPlan[] {
  return plans.map((p) => ({
    ...p,
    stops: p.stops.map((s) => {
      const mine = pending.filter((m) => m.stop_id === s.id);
      const checkin = mine.find((m) => m.entity === 'checkin');
      const outcome = [...mine].reverse().find((m) => m.entity === 'outcome');
      return { ...s, checkin_at: s.checkin_at ?? checkin?.client_ts ?? null, outcome: outcome?.outcome ?? s.outcome };
    }),
  }));
}

export function useOfflineDay() {
  const { api, queue, settings } = useSession();
  const [plans, setPlans] = useState<VisitPlan[]>([]);
  const [pending, setPending] = useState<SyncMutation[]>([]);
  const [online, setOnline] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<string | null>(null);

  const loadPending = useCallback(async () => setPending(await queue.pending()), [queue]);

  const sync = useCallback(async () => {
    setSyncing(true);
    setError(null);
    try {
      if ((await queue.pending()).length) await queue.flush(api, settings.deviceId);
      const today = indiaDate();
      // Today and upcoming assigned visits; finished and cancelled plans drop off.
      const fresh = (await api.visitPlans()).filter((p) => p.date >= today && !['completed', 'cancelled'].includes(p.state));
      fresh.sort((a, b) => (a.date + a.start_time).localeCompare(b.date + b.start_time));
      setPlans(fresh);
      await AsyncStorage.setItem(CACHE, JSON.stringify(fresh));
      setLastSync(new Date().toISOString());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Sync failed');
    } finally {
      setSyncing(false);
      await loadPending();
    }
  }, [api, queue, settings.deviceId, loadPending]);

  useEffect(() => {
    (async () => {
      const cached = await AsyncStorage.getItem(CACHE);
      if (cached) setPlans(JSON.parse(cached));
      await loadPending();
      sync();
    })();
    const offQueue = queue.subscribe(loadPending);
    const offNet = NetInfo.addEventListener((s) => {
      const isOnline = !!s.isConnected && s.isInternetReachable !== false;
      setOnline(isOnline);
      if (isOnline) sync();
    });
    return () => {
      offQueue();
      offNet();
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const record = useCallback(
    async (m: Omit<SyncMutation, 'idempotency_key' | 'client_ts'>) => {
      await queue.enqueue(m);
      if (online) sync();
    },
    [queue, online, sync],
  );

  return { plans: overlay(plans, pending), pending, online, syncing, error, lastSync, sync, record };
}
