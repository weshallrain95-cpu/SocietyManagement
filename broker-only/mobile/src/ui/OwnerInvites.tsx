// Broker side: owners who ticked "Allow this broker to handle my property" for this firm.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import type { OwnerInvite } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, inr } from '@/lib/format';
import { Button, Card, Chip, ErrorBox, H2, P, Row } from './components';

export function OwnerInvites() {
  const { api, role } = useSession();
  const q = useQuery({ queryKey: ['owner-invites'], queryFn: api.ownerInvites });
  if (!q.data?.length) return null;
  return (
    <>
      <H2>Owners inviting you</H2>
      {q.data.map((i) => <InviteCard key={i.id} i={i} canAnswer={role !== 'broker_staff'} />)}
    </>
  );
}

function InviteCard({ i, canAnswer }: { i: OwnerInvite; canAnswer: boolean }) {
  const { api } = useSession();
  const qc = useQueryClient();
  const answer = useMutation({
    mutationFn: (action: 'accept' | 'decline') => api.respondInvite(i.id, action),
    onSuccess: (r) => {
      qc.invalidateQueries({ queryKey: ['owner-invites'] });
      qc.invalidateQueries({ queryKey: ['listings'] });
      if (r.listing_id) router.push(`/listing/${r.listing_id}`);
    },
  });
  const t = i.terms;
  return (
    <Card>
      <Row style={{ justifyContent: 'space-between' }}>
        <P style={{ fontWeight: '700', flexShrink: 1 }}>{i.society}</P>
        <Chip label="Owner allowed you" tone="ok" />
      </Row>
      <P muted small>{i.building} · Flat {i.unit_no} · {bhk(i.bhk)} · {i.locality}</P>
      <P small>
        {i.owner_name} wants {i.txn_type === 'RENT' ? `rent ${inr(t.expected_rent, true)}` : `price ${inr(t.expected_price)}`}
        {t.deposit ? ` · deposit ${inr(t.deposit)}` : ''}{t.available_from ? ` · from ${t.available_from}` : ''}
      </P>
      {canAnswer ? (
        <Row>
          <Button small title="Accept — add to my flats" onPress={() => answer.mutate('accept')} busy={answer.isPending && answer.variables === 'accept'} testID="accept-invite" />
          <Button small kind="ghost" title="Decline" onPress={() => answer.mutate('decline')} />
        </Row>
      ) : <P small muted>Your Admin or a manager can accept this.</P>}
      {answer.error ? <ErrorBox error={answer.error} /> : null}
    </Card>
  );
}
