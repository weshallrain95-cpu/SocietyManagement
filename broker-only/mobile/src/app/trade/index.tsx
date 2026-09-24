// D17 co-broking hub: offers from fellow brokers (trade inbox), blasts I sent, and my list of fellow brokers.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';
import { Linking } from 'react-native';

import type { TradeAnswer, TradeDelivery } from '@/api';
import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, H2, Loading, P, Row, Screen } from '@/ui/components';

const ANSWER: Record<TradeAnswer, string> = { have_customer: 'You said: I have a customer', have_flat: 'You said: I have a flat', not_now: 'You said: not now' };

function Offer({ d }: { d: TradeDelivery }) {
  const { api } = useSession();
  const qc = useQueryClient();
  const reply = useMutation({
    mutationFn: (a: TradeAnswer) => api.replyTrade(d.id, a),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['trade-inbox'] }),
  });
  const yes: TradeAnswer = d.kind === 'flats' ? 'have_customer' : 'have_flat';
  return (
    <Card>
      <Row style={{ justifyContent: 'space-between' }}>
        <P style={{ fontWeight: '700', flexShrink: 1 }}>{d.from}</P>
        <Chip label={d.kind === 'flats' ? 'Ready flats' : 'Wanted'} tone={d.kind === 'flats' ? 'ok' : 'info'} />
      </Row>
      <P>{d.text}</P>
      <P small muted>{ago(d.created_at)}</P>
      {d.reply ? (
        <Chip label={ANSWER[d.reply]} tone="ok" />
      ) : (
        <Row style={{ flexWrap: 'wrap' }}>
          <Button small title={d.kind === 'flats' ? 'I have a customer' : 'I have a flat'} onPress={() => reply.mutate(yes)} busy={reply.isPending} testID={`reply-${d.id}`} />
          <Button small kind="ghost" title="Not now" onPress={() => reply.mutate('not_now')} />
        </Row>
      )}
      <Button small kind="secondary" title={`Call ${d.from_phone}`} onPress={() => Linking.openURL(`tel:${d.from_phone.replace(/\s/g, '')}`)} />
      {reply.error ? <ErrorBox error={reply.error} /> : null}
    </Card>
  );
}

export default function TradeHub() {
  const { api } = useSession();
  const inbox = useQuery({ queryKey: ['trade-inbox'], queryFn: api.tradeInbox });
  const sent = useQuery({ queryKey: ['trade-blasts'], queryFn: api.tradeBlasts, refetchInterval: 5000 });
  const contacts = useQuery({ queryKey: ['fellow-brokers'], queryFn: () => api.fellowBrokers() });
  const unread = inbox.data?.filter((d) => !d.read).length ?? 0;
  return (
    <Screen onRefresh={() => { inbox.refetch(); sent.refetch(); }} refreshing={inbox.isFetching}>
      <P muted>Share your ready flats with brokers you know, in and around the flat — or ask them for a flat your customer needs. They see the society, area, BHK and price; never the flat number, the owner or your customer.</P>
      <Button title="📢 Share flats with fellow brokers" onPress={() => router.push('/trade/blast?kind=flats')} testID="blast-flats" />
      <Button kind="secondary" title="🔎 Ask fellow brokers for a flat" onPress={() => router.push('/trade/blast?kind=requirement')} testID="blast-requirement" />
      <Card onPress={() => router.push('/trade/contacts')} testID="open-fellows">
        <Row style={{ justifyContent: 'space-between' }}>
          <P style={{ fontWeight: '700' }}>My fellow brokers</P>
          <Chip label={`${contacts.data?.length ?? 0}`} />
        </Row>
        <P small muted>Your own list: add names or import it from Excel or your phone contacts. Nobody else sees it.</P>
      </Card>

      <H2 right={unread ? <Chip label={`${unread} new`} tone="warn" /> : undefined}>Offers from fellow brokers</H2>
      {inbox.isLoading ? <Loading /> : inbox.error ? <ErrorBox error={inbox.error} /> : null}
      {inbox.data?.length === 0 ? <Empty title="Nothing yet" body="When a broker who has you in their list shares flats or asks for one, it lands here." /> : null}
      {inbox.data?.map((d) => <Offer key={d.id} d={d} />)}

      {sent.data?.length ? <H2>Sent by me</H2> : null}
      {sent.data?.map((b) => (
        <Card key={b.id} onPress={() => router.push(`/trade/${b.id}`)}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P small muted>{ago(b.created_at)} · {b.recipients_total} brokers</P>
            {b.replies_count ? <Chip label={`${b.replies_count} repl${b.replies_count === 1 ? 'y' : 'ies'}`} tone="ok" /> : null}
          </Row>
          <P>{b.text}</P>
        </Card>
      ))}
    </Screen>
  );
}
