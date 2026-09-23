import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { CONSENT_LABEL, phone } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, Field, Loading, P, Row, Screen } from '@/ui/components';

const SOURCE: Record<string, string> = {
  marketplace: 'App enquiry', phone_call: 'Phone call', walk_in: 'Walk-in', referral: 'Referral', board: 'Board', whatsapp_group: 'WhatsApp group', import: 'Imported', other: 'Other',
};

export default function Customers() {
  const { api } = useSession();
  const [q, setQ] = useState('');
  const query = useQuery({ queryKey: ['customers', q], queryFn: () => api.customers(q || undefined) });
  return (
    <Screen onRefresh={query.refetch} refreshing={query.isFetching}>
      <Button title="+ Add customer (walk-in / call)" onPress={() => router.push('/customer/new')} testID="add-customer" />
      <Field label="Search" placeholder="Name or mobile number" value={q} onChangeText={setQ} autoCorrect={false} />
      {query.isLoading ? <Loading /> : query.error ? <ErrorBox error={query.error} onRetry={query.refetch} /> : null}
      {query.data?.length === 0 ? <Empty title="No customers yet" body="Add walk-in and phone customers here — they don't need the app." /> : null}
      {query.data?.map((c) => (
        <Card key={c.id} onPress={() => router.push(`/customer/${c.id}`)}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700' }}>{c.name || phone(c.phone)}</P>
            <Chip label={SOURCE[c.source] ?? c.source} />
          </Row>
          <P muted small>{phone(c.phone)} · {c.stage.replace(/_/g, ' ')}</P>
          <P small style={{ color: c.can_message ? undefined : '#9A6200' }}>{CONSENT_LABEL[c.consent_state]}</P>
        </Card>
      ))}
    </Screen>
  );
}
