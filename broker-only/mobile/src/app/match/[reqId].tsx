import { useMutation, useQuery } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import type { Listing, MatchResult } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, chipIcon, indiaDate, inr } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Choice, Empty, ErrorBox, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';
import { FlatSearch } from '@/ui/FlatSearch';

function Result({ m, selected, onToggle }: { m: MatchResult; selected: boolean; onToggle?: () => void }) {
  const l = m.listing;
  return (
    <Card onPress={onToggle} style={selected ? { borderWidth: 2 } : undefined}>
      <Row style={{ justifyContent: 'space-between' }}>
        <P style={{ fontWeight: '700', flexShrink: 1 }}>{selected ? '☑ ' : m.excluded ? '' : '☐ '}{l.society}</P>
        {m.excluded ? <Chip label="Doesn't fit" tone="bad" /> : <Chip label={`${m.score}% match`} tone={m.score >= 80 ? 'ok' : 'warn'} />}
      </Row>
      <P muted small>{l.building} · {l.unit_no} · {bhk(l.bhk)} · {inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')}</P>
      <ChipRow>
        {m.explanation.map((c) => (
          <Chip key={c.key} label={`${chipIcon(c)} ${c.label}${c.detail ? `: ${c.detail}` : ''}`} tone={c.result === 'ok' ? 'ok' : c.result === 'fail' ? 'bad' : 'warn'} />
        ))}
      </ChipRow>
    </Card>
  );
}

export default function MatchScreen() {
  const { reqId, customerId } = useLocalSearchParams<{ reqId: string; customerId: string }>();
  const { api } = useSession();
  const [showExcluded, setShowExcluded] = useState(false);
  const [picked, setPicked] = useState<string[]>([]);
  const [ownPicks, setOwnPicks] = useState<Listing[]>([]); // flats the broker chose by name, outside the engine's list
  const [day, setDay] = useState<'today' | 'tomorrow'>('tomorrow');
  const [start, setStart] = useState('11:00');
  const q = useQuery({ queryKey: ['match', reqId, showExcluded], queryFn: () => api.match(reqId, showExcluded) });

  const shortlist = useMutation({
    mutationFn: async () => {
      const sl = await api.createShortlist(customerId, picked);
      await api.shareShortlist(sl.id);
      return sl;
    },
  });
  const plan = useMutation({
    mutationFn: () => {
      return api.createVisitPlan({ customer_id: customerId, listing_ids: picked, date: indiaDate(day === 'tomorrow' ? 1 : 0), start_time: start });
    },
    onSuccess: (p) => router.replace(`/visit/${p.id}`),
  });
  const toggle = (id: string) => setPicked((x) => (x.includes(id) ? x.filter((y) => y !== id) : [...x, id]));

  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      {q.data ? <P muted>{q.data.matched} of your flats fit · {q.data.considered} checked. Only your own inventory is searched.</P> : null}
      <Row>
        <Chip label="Fitting flats" selected={!showExcluded} onPress={() => setShowExcluded(false)} />
        <Chip label="Show why others don't fit" selected={showExcluded} onPress={() => setShowExcluded(true)} />
      </Row>
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {!showExcluded && q.data?.results.length === 0 ? <Empty title="No flats fit yet" body="Try a wider budget or area, or add more flats to your inventory." /> : null}
      {showExcluded && q.data && !q.data.results.some((m) => m.excluded) ? <Empty title="Every available flat fits" /> : null}
      {q.data?.results.filter((m) => m.excluded === showExcluded).map((m) => (
        <Result key={m.listing.id} m={m} selected={picked.includes(m.listing.id)} onToggle={m.excluded ? undefined : () => toggle(m.listing.id)} />
      ))}

      <H2>Have a flat in mind?</H2>
      {ownPicks.map((l) => (
        <Card key={l.id} onPress={() => { toggle(l.id); setOwnPicks((x) => x.filter((y) => y.id !== l.id)); }} style={{ borderWidth: 2 }}>
          <P style={{ fontWeight: '700' }}>☑ {l.society}</P>
          <P muted small>{l.building} · {l.unit_no} · {bhk(l.bhk)} · {inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')} · your pick</P>
        </Card>
      ))}
      <FlatSearch
        pickedIds={picked}
        onPick={(l) => {
          setPicked((x) => (x.includes(l.id) ? x : [...x, l.id]));
          if (!q.data?.results.some((m) => m.listing.id === l.id)) setOwnPicks((x) => [...x, l]);
        }}
      />

      {picked.length ? (
        <Card>
          <P style={{ fontWeight: '700' }}>{picked.length} flat{picked.length > 1 ? 's' : ''} selected</P>
          <Button kind="secondary" title="Share as WhatsApp shortlist" onPress={() => shortlist.mutate()} busy={shortlist.isPending} />
          {shortlist.isSuccess ? <Notice tone="ok">Shortlist sent. The customer can tap “Interested” on each flat — you’ll see it in their history.</Notice> : null}
          {shortlist.error ? <ErrorBox error={shortlist.error} /> : null}
          <Choice label="Plan a site visit" value={day} onChange={setDay} options={[{ value: 'today', label: 'Today' }, { value: 'tomorrow', label: 'Tomorrow' }]} />
          <Choice value={start} onChange={setStart} options={['10:00', '11:00', '15:00', '17:00'].map((t) => ({ value: t, label: t }))} />
          <Button title="Create visit plan" onPress={() => plan.mutate()} busy={plan.isPending} testID="create-plan" />
          {plan.error ? <ErrorBox error={plan.error} /> : null}
        </Card>
      ) : q.data?.matched ? <Notice>Tap flats to select them for a shortlist or a visit plan.</Notice> : null}
    </Screen>
  );
}
