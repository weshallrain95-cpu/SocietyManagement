import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Card, Chip, Empty, ErrorBox, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';
import { OwnerInvites } from '@/ui/OwnerInvites';

export default function Leads() {
  const { api } = useSession();
  const q = useQuery({ queryKey: ['leads'], queryFn: api.leads });
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <OwnerInvites />
      <H2>Customer enquiries</H2>
      <Notice>Enquiries from customers near your service area. You see how many of YOUR flats match; the customer sees your terms and rating.</Notice>
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {q.data?.length === 0 ? <Empty title="No enquiries yet" body="Customer enquiries in your area appear here. (If you went offline, go online again from More.)" /> : null}
      {q.data?.map((l) => (
        <Card key={l.id} onPress={() => router.push({ pathname: '/lead/[id]', params: { id: l.id, summary: l.summary, matches: String(l.match_count), mine: l.my_proposal ?? '' } })}>
          <Row style={{ justifyContent: 'space-between' }}>
            <Row>
              {l.urgency === 'urgent' ? <Chip label="Urgent" tone="bad" /> : null}
              <Chip label={`${l.match_count} of your flats match`} tone={l.match_count ? 'ok' : undefined} />
            </Row>
            <P muted small>{ago(l.created_at)}</P>
          </Row>
          <P>{l.summary}</P>
          {l.my_proposal ? <P small muted>Your proposal: {l.my_proposal}</P> : <P small style={{ fontWeight: '600' }}>Tap to respond</P>}
        </Card>
      ))}
    </Screen>
  );
}
