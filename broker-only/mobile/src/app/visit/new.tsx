// Plan a site visit by picking flats yourself (society + flat number), without the matching engine.
import { useMutation, useQuery } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import type { Listing } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, indiaDate } from '@/lib/format';
import { Button, Card, Choice, ErrorBox, H2, Notice, P, Row, Screen } from '@/ui/components';
import { FlatSearch } from '@/ui/FlatSearch';

export default function NewVisitPlan() {
  const { customerId, customerName, listingId } = useLocalSearchParams<{ customerId: string; customerName?: string; listingId?: string }>();
  const { api } = useSession();
  // Opened from a flat's page: that flat is already on the list.
  const pre = useQuery({ queryKey: ['listing', listingId], queryFn: () => api.listing(listingId!), enabled: !!listingId });
  const [dropPre, setDropPre] = useState(false);
  const [added, setAdded] = useState<Listing[]>([]);
  const picked = [...(pre.data && !dropPre ? [pre.data] : []), ...added.filter((l) => l.id !== pre.data?.id)];
  const setPicked = (f: (x: Listing[]) => Listing[]) => {
    const next = f(picked);
    if (pre.data && !next.some((l) => l.id === pre.data!.id)) setDropPre(true);
    setAdded(next.filter((l) => l.id !== pre.data?.id));
  };
  const [day, setDay] = useState<'today' | 'tomorrow'>('tomorrow');
  const [start, setStart] = useState('11:00');
  const plan = useMutation({
    mutationFn: () => api.createVisitPlan({ customer_id: customerId, listing_ids: picked.map((l) => l.id), date: indiaDate(day === 'tomorrow' ? 1 : 0), start_time: start }),
    onSuccess: (p) => router.replace(`/visit/${p.id}`),
  });

  return (
    <Screen>
      <P muted>{customerName ? `For ${customerName}. ` : ''}Type the society and flat number you want to show — the way you always have. We’ll work out the route.</P>
      <FlatSearch pickedIds={picked.map((l) => l.id)} onPick={(l) => setPicked((x) => [...x, l])} />

      <H2>{picked.length ? `${picked.length} flat${picked.length > 1 ? 's' : ''} to visit` : 'No flats picked yet'}</H2>
      {picked.map((l, i) => (
        <Card key={l.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{i + 1}. {l.society}</P>
            <Button small kind="ghost" title="Remove" onPress={() => setPicked((x) => x.filter((y) => y.id !== l.id))} />
          </Row>
          <P muted small>{l.building} · Flat {l.unit_no} · {bhk(l.bhk)}</P>
        </Card>
      ))}
      {picked.length ? (
        <>
          <Choice label="When" value={day} onChange={setDay} options={[{ value: 'today', label: 'Today' }, { value: 'tomorrow', label: 'Tomorrow' }]} />
          <Choice value={start} onChange={setStart} options={['10:00', '11:00', '15:00', '17:00'].map((t) => ({ value: t, label: t }))} />
          <Button title="Create visit plan" onPress={() => plan.mutate()} busy={plan.isPending} testID="create-own-plan" />
          {plan.error ? <ErrorBox error={plan.error} /> : null}
        </>
      ) : <Notice>Tip: “1203” alone lists every flat 1203 you have; a society name alone lists all your flats there.</Notice>}
    </Screen>
  );
}
