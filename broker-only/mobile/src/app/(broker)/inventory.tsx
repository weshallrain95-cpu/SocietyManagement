import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { bhk, inr, statusTone } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Empty, ErrorBox, Loading, P, Row, Screen } from '@/ui/components';

const FILTERS = [
  { key: '', label: 'All' },
  { key: 'AVAILABLE,AVAILABLE_UNCONFIRMED', label: 'Available' },
  { key: 'ON_HOLD', label: 'On hold' },
  { key: 'LET,SOLD', label: 'Let / sold' },
];

export default function Inventory() {
  const { api } = useSession();
  const [filter, setFilter] = useState('');
  const q = useQuery({ queryKey: ['listings', filter], queryFn: () => api.listings(filter ? { status: filter } : undefined) });
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <Button title="+ Add flat" onPress={() => router.push('/listing/new')} testID="add-flat" />
      <ChipRow>
        {FILTERS.map((f) => <Chip key={f.key} label={f.label} selected={filter === f.key} onPress={() => setFilter(f.key)} />)}
      </ChipRow>
      <P small muted>Only you and your team can see these flats. Other brokers never see your inventory.</P>
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {q.data?.length === 0 ? <Empty title="No flats here" body="Add a flat, or upload your Excel from the desktop console." /> : null}
      {q.data?.map((l) => (
        <Card key={l.id} onPress={() => router.push(`/listing/${l.id}`)}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{l.society}</P>
            <P style={{ fontWeight: '700' }}>{inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')}</P>
          </Row>
          <P muted small>{l.building} · Flat {l.unit_no} · {bhk(l.bhk)}{l.floor !== null ? ` · Floor ${l.floor}` : ''}</P>
          <Row>
            <Chip label={l.status_label} tone={statusTone(l.status)} />
            {l.stale ? <Chip label="Reconfirm" tone="warn" /> : null}
            {l.owner_withdrew ? <Chip label="Owner removed you" tone="bad" /> : l.owner_appointed ? <Chip label="Owner-appointed" tone="ok" /> : null}
          </Row>
        </Card>
      ))}
    </Screen>
  );
}
