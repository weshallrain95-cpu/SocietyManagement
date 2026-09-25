// One request and the brokers' offers, best first (MKT-07). The customer accepts up to 3 (MKT-08); accepted
// brokers get the customer's number and call them. The customer can close the request at any time (MKT-09).
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React from 'react';
import { Alert, Platform, Text, View } from 'react-native';

import type { Proposal } from '@/api';
import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';
import { usePalette } from '@/ui/theme';
import { ENQUIRY_STATE } from '../(customer)/find';

const MAX_ACCEPTED = 3;

function responseText(s: number | null) {
  if (!s) return '';
  return s < 3600 ? `replies in ~${Math.max(1, Math.round(s / 60))} min` : `replies in ~${Math.round(s / 3600)} h`;
}

function confirm(message: string, onYes: () => void) {
  if (Platform.OS === 'web') {
    if (window.confirm(message)) onYes();
  } else {
    Alert.alert('Please confirm', message, [{ text: 'No', style: 'cancel' }, { text: 'Yes', onPress: onYes }]);
  }
}

export default function EnquiryScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['enquiry', id], queryFn: () => api.enquiry(id), refetchInterval: 15000 });
  const done = () => {
    qc.invalidateQueries({ queryKey: ['my-enquiries'] });
    q.refetch();
  };
  const accept = useMutation({ mutationFn: (pid: string) => api.acceptProposal(pid), onSuccess: done });
  const close = useMutation({ mutationFn: (state: 'cancelled' | 'fulfilled') => api.closeEnquiry(id, state), onSuccess: done });

  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (q.error || !q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const e = q.data;
  const live = e.state === 'open' || e.state === 'in_progress';
  const accepted = e.proposals.filter((p) => p.state === 'accepted').length;
  const st = ENQUIRY_STATE[e.state];

  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <Card>
        <P style={{ fontWeight: '700' }}>{e.summary}</P>
        <Row style={{ flexWrap: 'wrap' }}>
          <Chip label={st?.label ?? e.state} tone={st?.tone} />
          <P small muted>sent to {e.recipients} brokers · {ago(e.created_at)}</P>
        </Row>
      </Card>

      <H2>Offers from brokers {e.proposals.length ? `(${e.proposals.length})` : ''}</H2>
      {!e.proposals.length && live ? <Empty title="Waiting for offers" body="Brokers usually reply within the hour. This page updates by itself." /> : null}
      {live && e.proposals.length ? <P small muted>Accept up to {MAX_ACCEPTED} brokers. They get your number and call you. {accepted ? `${accepted} of ${MAX_ACCEPTED} accepted.` : ''}</P> : null}
      {accept.error ? <ErrorBox error={accept.error} /> : null}
      {e.proposals.map((p) => (
        <Offer
          key={p.id}
          p={p}
          canAccept={live && p.state === 'sent' && accepted < MAX_ACCEPTED}
          busy={accept.isPending && accept.variables === p.id}
          onAccept={() => confirm(`Share your number with ${p.broker.name}? They will call you about flats.`, () => accept.mutate(p.id))}
        />
      ))}

      {live ? (
        <>
          <H2>Done looking?</H2>
          {close.error ? <ErrorBox error={close.error} /> : null}
          <Row>
            <Button small title="I found a flat" onPress={() => close.mutate('fulfilled')} busy={close.isPending && close.variables === 'fulfilled'} />
            <Button small kind="ghost" title="Cancel request" onPress={() => confirm('Cancel this request? Brokers stop sending offers.', () => close.mutate('cancelled'))} />
          </Row>
        </>
      ) : (
        <Button kind="secondary" title="Post a new requirement" onPress={() => router.replace('/enquiry/new')} />
      )}
    </Screen>
  );
}

function Offer({ p, canAccept, busy, onAccept }: { p: Proposal; canAccept: boolean; busy: boolean; onAccept: () => void }) {
  const c = usePalette();
  const rating = Number(p.broker.rating_bayes);
  return (
    <Card>
      <Row style={{ justifyContent: 'space-between' }}>
        <View style={{ flex: 1, gap: 2 }}>
          <Text style={{ fontSize: 16, fontWeight: '800', color: c.text }}>{p.broker.name}</Text>
          <P small muted>
            {p.broker.rating_count ? `★ ${rating.toFixed(1)} (${p.broker.rating_count})` : 'New on Only Broker'}
            {p.broker.closures ? ` · ${p.broker.closures} deals` : ''}
            {p.broker.median_response_s ? ` · ${responseText(p.broker.median_response_s)}` : ''}
          </P>
        </View>
        {p.broker.rera_registered ? <Chip label="RERA ✓" tone="ok" /> : null}
      </Row>
      {p.promoted ? <Chip label="Promoted" tone="warn" /> : null}
      <Row style={{ flexWrap: 'wrap' }}>
        <Chip label={`${p.match_count} matching flat${p.match_count === 1 ? '' : 's'}`} tone={p.match_count ? 'info' : undefined} />
        <Chip label={`Fee: ${p.brokerage_terms}`} />
      </Row>
      {p.message ? <P>“{p.message}”</P> : null}
      {p.state === 'accepted' ? (
        <Notice tone="ok">Accepted. {p.broker.name} has your number and will call you.</Notice>
      ) : canAccept ? (
        <Button title="Accept and share my number" onPress={onAccept} busy={busy} testID={`accept-${p.id}`} />
      ) : null}
    </Card>
  );
}
