// The broker's own list of fellow brokers (channel partners): their asset, private to their firm.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, Field, H2, Loading, P, Row, Screen } from '@/ui/components';
import { ImportPanel } from '@/ui/ImportPanel';

export default function FellowBrokers() {
  const { api } = useSession();
  const qc = useQueryClient();
  const [q, setQ] = useState('');
  const list = useQuery({ queryKey: ['fellow-brokers', q], queryFn: () => api.fellowBrokers(q || undefined) });
  const refresh = () => qc.invalidateQueries({ queryKey: ['fellow-brokers'] });
  const [name, setName] = useState('');
  const [firm, setFirm] = useState('');
  const [mobile, setMobile] = useState('');
  const [area, setArea] = useState('');
  const add = useMutation({
    mutationFn: () => api.addFellowBroker({ name, firm, phone: indianMobile(mobile)!, area }),
    onSuccess: () => { setName(''); setFirm(''); setMobile(''); setArea(''); refresh(); },
  });
  const remove = useMutation({ mutationFn: api.removeFellowBroker, onSuccess: refresh });

  return (
    <Screen onRefresh={list.refetch} refreshing={list.isFetching}>
      <P muted>Brokers you trade with. Their office area decides who is “in and around” a flat when you share it. Nobody else sees this list.</P>
      <H2>My list ({list.data?.length ?? 0})</H2>
      <Field label="Search" placeholder="Name, agency, area or number" value={q} onChangeText={setQ} autoCorrect={false} />
      {list.isLoading ? <Loading /> : list.error ? <ErrorBox error={list.error} onRetry={list.refetch} /> : null}
      {list.data?.length === 0 ? <Empty title="No fellow brokers yet" body="Import your list or add them one by one." /> : null}
      {list.data?.map((c) => (
        <Card key={c.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{c.name}</P>
            {c.on_platform ? <Chip label="On the app" tone="ok" /> : null}
          </Row>
          <P small muted>{[c.firm !== c.name ? c.firm : '', c.phone, c.locality ?? (c.address || 'area not known')].filter(Boolean).join(' · ')}</P>
          <Button small kind="ghost" title="Remove" onPress={() => remove.mutate(c.id)} />
        </Card>
      ))}
      <H2>Add fellow brokers</H2>
      <ImportPanel what="fellow brokers" columns="Name, Agency, Mobile, Area" run={api.importFellowBrokers} onDone={refresh} />

      <Card>
        <P style={{ fontWeight: '700' }}>Add one</P>
        <Field label="Name" value={name} onChangeText={setName} />
        <Field label="Agency (optional)" value={firm} onChangeText={setFirm} />
        <Field label="Mobile number" keyboardType="phone-pad" value={mobile} onChangeText={setMobile} />
        <Field label="Office area" placeholder="e.g. Manpada, Kolshet Road" value={area} onChangeText={setArea} hint="Used to find brokers in and around a flat." />
        <Button title="Add" onPress={() => add.mutate()} disabled={!name.trim() || !indianMobile(mobile)} busy={add.isPending} testID="add-fellow" />
        {add.error ? <ErrorBox error={add.error} /> : null}
      </Card>

    </Screen>
  );
}
