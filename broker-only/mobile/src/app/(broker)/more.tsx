import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { ROLE_LABEL, useAgency } from '@/auth/useAgency';
import { Button, Card, Chip, H2, P, Row, Screen } from '@/ui/components';
import { SwitchMode } from '@/ui/SwitchMode';
import { TeamSection } from '@/ui/TeamSection';

export default function More() {
  const { api, signOut, settings } = useSession();
  const qc = useQueryClient();
  const a = useAgency();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me });
  const inbox = useQuery({ queryKey: ['trade-inbox'], queryFn: api.tradeInbox });
  // Online for customer enquiries from sign-up; going offline is the broker's choice and is remembered.
  const status = useQuery({ queryKey: ['presence'], queryFn: api.presenceStatus });
  const online = status.data?.online ?? true;
  const presence = useMutation({ mutationFn: (on: boolean) => api.presence(on), onSuccess: () => status.refetch() });
  const org = me.data?.memberships.find((m) => m.org_id === me.data?.active_org_id);

  return (
    <Screen onRefresh={() => qc.invalidateQueries()} refreshing={false}>
      <Card>
        <P style={{ fontWeight: '700' }}>{org?.org_name ?? 'Your agency'}</P>
        <P muted small>{me.data?.display_name} · {me.data?.phone_masked} · {ROLE_LABEL[org?.role ?? ''] ?? ''}</P>
        {settings.demo ? <Chip label="Demo mode" tone="warn" /> : null}
      </Card>

      <Card onPress={() => router.push('/agency/details')} testID="open-agency-details">
        <P style={{ fontWeight: '700' }}>Agency details</P>
        <P small muted>Business, owners, PAN / GST / MahaRERA, office{a.isAdmin ? ' — you can edit these' : ''}.</P>
      </Card>

      <H2>Trade with fellow brokers</H2>
      <Card onPress={() => router.push('/trade')} testID="open-trade">
        <Row style={{ justifyContent: 'space-between' }}>
          <P style={{ fontWeight: '700' }}>Co-broking</P>
          {inbox.data?.filter((d) => !d.read).length ? <Chip label={`${inbox.data.filter((d) => !d.read).length} new`} tone="warn" /> : null}
        </Row>
        <P small muted>Share ready flats with brokers you know, ask them for a flat, and see their offers.</P>
      </Card>

      <H2>Receive enquiries</H2>
      <Card>
        <Row style={{ justifyContent: 'space-between' }}>
          <P>{online ? 'You are online — customer enquiries in your area reach you.' : 'You are offline — you get no new customer enquiries until you go online again.'}</P>
        </Row>
        <Button title={online ? 'Go offline' : 'Go online'} kind={online ? 'secondary' : 'primary'} onPress={() => presence.mutate(!online)} busy={presence.isPending} />
      </Card>

      <H2>Team</H2>
      <TeamSection />

      <SwitchMode current="broker" />

      <H2>App</H2>
      <Button kind="secondary" title="Server settings" onPress={() => router.push('/settings')} />
      <Button kind="danger" title="Sign out" onPress={async () => { await signOut(); router.replace('/login'); }} />
    </Screen>
  );
}
