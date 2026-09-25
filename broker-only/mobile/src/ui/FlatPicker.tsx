// Tick flats from the broker's own "Available now" list (only theirs; the app never offers anyone else's flat).
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';

import type { Listing } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, inr } from '@/lib/format';
import { Card, Field, Loading, Notice, P, Tick } from './components';

export function FlatPicker({ picked, onChange, max = 10, label = 'Which of your flats?' }: {
  picked: string[];
  onChange: (ids: string[], listings: Listing[]) => void;
  max?: number;
  label?: string;
}) {
  const { api } = useSession();
  const [q, setQ] = useState('');
  const r = useQuery({ queryKey: ['listings', 'open'], queryFn: () => api.listings() });
  const all = (r.data ?? []).filter((l) => l.available_now && !l.owner_withdrew);
  const n = q.trim().toLowerCase();
  const shown = all.filter((l) => !n || `${l.society} ${l.building} ${l.unit_no}`.toLowerCase().includes(n));
  const toggle = (l: Listing, on: boolean) => {
    const ids = on ? [...picked, l.id].slice(0, max) : picked.filter((x) => x !== l.id);
    onChange(ids, all.filter((x) => ids.includes(x.id)));
  };
  return (
    <>
      <P small style={{ fontWeight: '600' }}>{label} {picked.length ? `(${picked.length} picked)` : ''}</P>
      {all.length > 6 ? <Field label="Filter" placeholder="Society or flat number" value={q} onChangeText={setQ} autoCapitalize="none" /> : null}
      {r.isLoading ? <Loading /> : null}
      {shown.slice(0, 30).map((l) => (
        <Card key={l.id}>
          <Tick
            checked={picked.includes(l.id)}
            onChange={(on) => toggle(l, on)}
            label={`${l.society} · ${l.building} ${l.unit_no} · ${bhk(l.bhk)} · ${inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')}`}
            testID={`tick-${l.unit_no}`}
          />
        </Card>
      ))}
      {r.data && !all.length ? <Notice>Nothing in your “Available now” list yet. Pick flats from Flats → All flats.</Notice> : null}
      {picked.length >= max ? <P small muted>At most {max} flats in one message.</P> : null}
    </>
  );
}
