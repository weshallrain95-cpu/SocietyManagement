// "Society + flat number" search for staff who already know which flat they want to show.
// Works alongside the matching engine: brokers keep their own way of picking flats until they trust it.
// Only the broker's own flats are searched. The app never offers a flat that isn't in their list.
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';

import type { Listing } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, inr } from '@/lib/format';
import { useDebounced } from '@/lib/useDebounced';
import { Button, Card, Field, Loading, Notice, P, Row } from './components';

export function FlatSearch({ pickedIds, onPick, label = 'Society and flat number' }: {
  pickedIds: string[];
  onPick: (l: Listing) => void;
  label?: string;
}) {
  const { api } = useSession();
  const [q, setQ] = useState('');
  const term = useDebounced(q.trim(), 300);
  const r = useQuery({ queryKey: ['flat-search', term], queryFn: () => api.searchFlats(term), enabled: term.length >= 2 || /\d/.test(term) });
  const d = r.data;

  return (
    <>
      <Field label={label} placeholder="e.g. HE A-1203 · Rodas B 502 · 1203" value={q} onChangeText={setQ} autoCorrect={false} autoCapitalize="none" testID="flat-search" hint="Nicknames and spelling mistakes are fine." />
      {r.isFetching && !d ? <Loading /> : null}
      {d?.results.map((l) => {
        const picked = pickedIds.includes(l.id);
        return (
          <Card key={l.id}>
            <Row style={{ justifyContent: 'space-between' }}>
              <P style={{ fontWeight: '700', flexShrink: 1 }}>{l.society}</P>
              <Button small kind={picked ? 'ghost' : 'secondary'} title={picked ? 'Added ✓' : 'Add'} disabled={picked} onPress={() => onPick(l)} testID={`pick-${l.unit_no}`} />
            </Row>
            <P muted small>{l.building} · Flat {l.unit_no} · {bhk(l.bhk)} · {inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')} · {l.status_label}</P>
          </Card>
        );
      })}
      {d && term && !d.results.length ? (
        <Notice>None of your flats matches “{term}”. Only flats in your own list can be added to a visit.</Notice>
      ) : null}
    </>
  );
}
