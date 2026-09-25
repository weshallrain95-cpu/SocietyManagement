import { useMutation, useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { Button, Card, Chip, Choice, ErrorBox, Field, H2, Notice, P, Row, Screen } from '@/ui/components';

export default function More() {
  const { api, signOut, settings } = useSession();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me });
  const staff = useQuery({ queryKey: ['staff'], queryFn: api.staff });
  const inbox = useQuery({ queryKey: ['trade-inbox'], queryFn: api.tradeInbox });
  // Online for customer enquiries from sign-up; going offline is the broker's choice and is remembered.
  const status = useQuery({ queryKey: ['presence'], queryFn: api.presenceStatus });
  const online = status.data?.online ?? true;
  const presence = useMutation({ mutationFn: (on: boolean) => api.presence(on), onSuccess: () => status.refetch() });
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<'broker_staff' | 'broker_manager'>('broker_staff');
  const invite = useMutation({
    mutationFn: () => api.inviteStaff({ phone: indianMobile(phone)!, display_name: name, role }),
    onSuccess: () => {
      setPhone('');
      setName('');
      staff.refetch();
    },
  });
  const org = me.data?.memberships.find((m) => m.org_id === me.data?.active_org_id);

  return (
    <Screen>
      <Card>
        <P style={{ fontWeight: '700' }}>{org?.org_name ?? 'Your agency'}</P>
        <P muted small>{me.data?.display_name} · {me.data?.phone_masked} · {org?.role.replace('broker_', '')}</P>
        {settings.demo ? <Chip label="Demo mode" tone="warn" /> : null}
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
      {staff.data?.map((m) => (
        <Card key={m.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P>{m.name || 'Team member'}</P>
            <Chip label={m.role.replace('broker_', '')} />
          </Row>
        </Card>
      ))}
      <Card>
        <P style={{ fontWeight: '600' }}>Add a team member</P>
        <Field label="Mobile number" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
        <Field label="Name" value={name} onChangeText={setName} />
        <Choice value={role} onChange={setRole} options={[{ value: 'broker_staff', label: 'Field staff' }, { value: 'broker_manager', label: 'Manager' }]} />
        <Button title="Add" onPress={() => invite.mutate()} disabled={!indianMobile(phone)} busy={invite.isPending} />
        {invite.error ? <ErrorBox error={invite.error} /> : null}
        <Notice>Field staff see only the visits you assign them, with owner numbers hidden.</Notice>
      </Card>

      <H2>App</H2>
      <Button kind="secondary" title="Server settings" onPress={() => router.push('/settings')} />
      <Button kind="danger" title="Sign out" onPress={async () => { await signOut(); router.replace('/login'); }} />
    </Screen>
  );
}
