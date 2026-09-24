// A blast I sent to fellow brokers, and who replied.
import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React from 'react';
import { Linking } from 'react-native';

import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Button, Card, Empty, ErrorBox, H2, Loading, P, Row, Screen } from '@/ui/components';

export default function TradeBlastDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const q = useQuery({ queryKey: ['trade-blast', id], queryFn: () => api.tradeBlast(id), refetchInterval: 5000 });
  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (q.error || !q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const b = q.data;
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <Card>
        <P small muted>{ago(b.created_at)} · {b.recipients_total} brokers · {b.delivered_in_app} in the app · {b.via_whatsapp} by WhatsApp</P>
        <P>{b.text}</P>
      </Card>
      <H2>Replies</H2>
      {!b.replies?.length ? <Empty title="No replies yet" body="Brokers who have a customer (or a flat) reply here. Pull down to refresh." /> : null}
      {b.replies?.map((r, i) => (
        <Card key={i}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{r.from}</P>
            <P small muted>{ago(r.at)}</P>
          </Row>
          {r.message ? <P>{r.message}</P> : null}
          <Button small kind="secondary" title={`Call ${r.phone}`} onPress={() => Linking.openURL(`tel:${r.phone.replace(/\s/g, '')}`)} />
        </Card>
      ))}
    </Screen>
  );
}
