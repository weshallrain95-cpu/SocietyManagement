// OWN-01/02: brokers who work near the owner's flat. Nothing reaches a broker until the owner ticks
// "Allow this broker to handle my property" (founder decision A).
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import type { NearbyBroker } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Card, Chip, Empty, ErrorBox, Loading, Notice, P, Row, Screen, Tick } from '@/ui/components';

export default function BrokersNearby() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const q = useQuery({ queryKey: ['brokers-nearby', id], queryFn: () => api.brokersNearby(id) });
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <P muted>Verified brokers who work around your flat, best rated first. Invite as many as you like — each one needs your tick.</P>
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {q.data?.length === 0 ? <Empty title="No verified brokers nearby yet" body="We’re adding brokers in your area. Check again soon." /> : null}
      {q.data?.map((b) => <BrokerCard key={b.org_id} flatId={id} b={b} />)}
    </Screen>
  );
}

function BrokerCard({ flatId, b }: { flatId: string; b: NearbyBroker }) {
  const { api } = useSession();
  const qc = useQueryClient();
  const [allow, setAllow] = useState(false);
  const invite = useMutation({
    mutationFn: () => api.inviteBroker(flatId, b.org_id, allow),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['owner-flat', flatId] }),
  });
  return (
    <Card>
      <Row style={{ justifyContent: 'space-between' }}>
        <P style={{ fontWeight: '700', flexShrink: 1 }}>{b.name}</P>
        {b.rera_verified ? <Chip label="RERA checked" tone="ok" /> : null}
      </Row>
      <P small muted>
        {b.rating_count ? `★ ${b.rating.toFixed(1)} from ${b.rating_count} reviews` : 'No reviews yet'}
        {b.closures ? ` · ${b.closures} deals closed` : ''}
        {b.median_response_min != null ? ` · replies in ~${b.median_response_min} min` : ''}
      </P>
      {b.serving ? <Notice tone="ok">Already handling your flat.</Notice> : invite.isSuccess ? (
        <Notice tone="ok">Invitation sent. {b.name} will accept or decline; you’ll see it on your flat’s page.</Notice>
      ) : (
        <>
          {b.withdrawn ? <Notice tone="warn">You removed this broker earlier. Inviting them allows them again.</Notice> : null}
          <Tick label="Allow this broker to handle my property" checked={allow} onChange={setAllow} testID={`allow-invite-${b.name}`} />
          <Button small title="Invite" disabled={!allow} onPress={() => invite.mutate()} busy={invite.isPending} testID={`invite-${b.name}`} />
        </>
      )}
      {invite.error ? <ErrorBox error={invite.error} /> : null}
    </Card>
  );
}
