import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { indiaDate, time } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Empty, ErrorBox, H2, Loading, P, Row, Screen, Stat } from '@/ui/components';


export default function Today() {
  const { api, settings } = useSession();
  const plans = useQuery({ queryKey: ['plans', indiaDate()], queryFn: () => api.visitPlans(indiaDate()) });
  const leads = useQuery({ queryKey: ['leads'], queryFn: api.leads });
  const listings = useQuery({ queryKey: ['listings'], queryFn: () => api.listings() });
  const refreshing = plans.isFetching || leads.isFetching || listings.isFetching;
  const refetch = () => Promise.all([plans.refetch(), leads.refetch(), listings.refetch()]);

  const newLeads = leads.data?.filter((l) => !l.my_proposal && l.state === 'open').length ?? 0;
  const stale = listings.data?.filter((l) => l.stale) ?? [];
  const available = listings.data?.filter((l) => l.status === 'AVAILABLE' || l.status === 'AVAILABLE_UNCONFIRMED').length ?? 0;

  return (
    <Screen onRefresh={refetch} refreshing={refreshing}>
      {settings.demo ? <Chip label="Demo data" tone="warn" /> : null}
      <Row style={{ flexWrap: 'wrap' }}>
        <Stat label="New leads" value={newLeads} tone={newLeads ? 'accent' : undefined} />
        <Stat label="Visits today" value={plans.data?.reduce((n, p) => n + p.stops.length, 0) ?? '–'} />
        <Stat label="Flats available" value={available} />
      </Row>

      <H2 right={<Button small kind="ghost" title="+ Customer" onPress={() => router.push('/customer/new')} />}>Today’s visits</H2>
      {plans.isLoading ? <Loading /> : plans.error ? <ErrorBox error={plans.error} onRetry={plans.refetch} /> : null}
      {plans.data?.length === 0 ? <Empty title="No visits today" body="Match a customer's requirement to plan a tour." /> : null}
      {plans.data?.map((p) => (
        <Card key={p.id} onPress={() => router.push(`/visit/${p.id}`)}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700' }}>{p.customer_name || 'Customer'}</P>
            <Chip label={p.state.replace(/_/g, ' ')} tone={p.state === 'customer_confirmed' ? 'ok' : 'info'} />
          </Row>
          <P muted small>
            {p.start_time.slice(0, 5)} · {p.stops.length} flats · {p.total_travel_min ?? '?'} min travel
          </P>
          <ChipRow>
            {p.stops.map((s) => (
              <Chip key={s.id} label={`${time(s.slot_start)} ${s.society}`} tone={s.outcome ? 'ok' : undefined} />
            ))}
          </ChipRow>
        </Card>
      ))}

      {stale.length ? (
        <>
          <H2>Reconfirm availability</H2>
          <Card onPress={() => router.push('/inventory')}>
            <P>{stale.length} flat{stale.length > 1 ? 's have' : ' has'} not been reconfirmed recently.</P>
            <P muted small>Stale flats drop in matching and customers see them as unconfirmed. One tap each to reconfirm.</P>
          </Card>
        </>
      ) : null}

      <H2>Quick actions</H2>
      <Row style={{ flexWrap: 'wrap' }}>
        <Button small kind="secondary" title="Add flat" onPress={() => router.push('/listing/new')} />
        <Button small kind="secondary" title="Walk-in customer" onPress={() => router.push('/customer/new')} />
        <Button small kind="secondary" title="Open leads" onPress={() => router.push('/leads')} />
      </Row>
    </Screen>
  );
}
