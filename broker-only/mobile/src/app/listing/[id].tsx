import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React from 'react';
import { Alert, Platform } from 'react-native';

import { useSession } from '@/auth/session';
import { bhk, inr, statusTone } from '@/lib/format';
import { Button, Card, Chip, ChipRow, ErrorBox, H1, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';

const KEY_LABEL: Record<string, string> = { office: 'At my office', owner: 'With the owner', staff: 'With field staff', society_office: 'Society office', lockbox: 'Lock-box', neighbour: 'Neighbour' };

function confirm(msg: string, ok: () => void) {
  if (Platform.OS === 'web') {
    if (globalThis.confirm?.(msg) ?? true) ok();
    return;
  }
  Alert.alert('Please confirm', msg, [{ text: 'Cancel', style: 'cancel' }, { text: 'Yes', onPress: ok }]);
}

export default function ListingDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['listing', id], queryFn: () => api.listing(id) });
  const status = useMutation({
    mutationFn: (b: { state: string; on_behalf_of_owner?: boolean }) => api.reportStatus(id, b),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['listing', id] });
      qc.invalidateQueries({ queryKey: ['listings'] });
    },
  });
  const reconfirm = useMutation({ mutationFn: () => api.reconfirm(id), onSuccess: () => q.refetch() });

  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (q.error || !q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const l = q.data;
  const rent = l.txn_type === 'RENT';
  const open = l.status === 'AVAILABLE' || l.status === 'AVAILABLE_UNCONFIRMED';
  const attrs = Object.entries(l.attributes ?? {});

  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <H1>{l.society}</H1>
      <P muted>{l.building} · Flat {l.unit_no} · {bhk(l.bhk)}{l.floor !== null ? ` · Floor ${l.floor}` : ''}</P>
      <Row style={{ flexWrap: 'wrap' }}>
        <Chip label={l.status_label} tone={statusTone(l.status)} />
        <Chip label={`${inr(l.asking_rent ?? l.asking_price, rent)}`} />
        {l.deposit ? <Chip label={`Deposit ${inr(l.deposit)}`} /> : null}
      </Row>

      <H2>Status</H2>
      {l.status === 'AVAILABLE_UNCONFIRMED' ? <Notice tone="warn">Waiting for the owner’s YES. Owners confirm from a WhatsApp link — no app needed.</Notice> : null}
      <Row style={{ flexWrap: 'wrap' }}>
        {open ? (
          <>
            <Button small kind="secondary" title="Reconfirm available" onPress={() => reconfirm.mutate()} busy={reconfirm.isPending} />
            <Button small kind="secondary" title="Token / on hold" onPress={() => status.mutate({ state: 'ON_HOLD' })} />
            <Button small kind="danger" title={rent ? 'Rented out' : 'Sold'} onPress={() => confirm(`Mark this flat as ${rent ? 'rented out' : 'sold'}? Other brokers listing it will see the change (not who made it).`, () => status.mutate({ state: rent ? 'LET' : 'SOLD' }))} />
          </>
        ) : (
          <>
            <Button small title="Available again" onPress={() => status.mutate({ state: 'AVAILABLE' })} />
            <Button small kind="secondary" title="Owner confirmed on phone" onPress={() => confirm('Record that the owner told you on the phone that the flat is available?', () => status.mutate({ state: 'AVAILABLE', on_behalf_of_owner: true }))} />
          </>
        )}
      </Row>
      {status.data ? <P small muted>Now: {status.data.label}</P> : null}
      {status.error ? <ErrorBox error={status.error} /> : null}

      <H2>Keys & owner</H2>
      <Card>
        <P>Keys: {l.keys ? KEY_LABEL[l.keys.holder_type] ?? l.keys.holder_type : 'not recorded'}{l.keys?.needs_handover ? ' — needs handover' : ''}</P>
        {l.keys?.instructions ? <P muted small>{l.keys.instructions}</P> : null}
        <P>Owner: {l.owner_name || '—'} {l.owner_phone ? `· ${l.owner_phone}` : ''}</P>
        <P muted small>Private to your agency.</P>
      </Card>

      <H2>What we know about this flat</H2>
      {attrs.length === 0 ? <P muted small>No details yet. Details from the owner, other sources and site visits appear here.</P> : null}
      <ChipRow>
        {attrs.map(([k, a]) => (
          <Chip key={k} label={`${k.replace(/^furn_/, '').replace(/_/g, ' ')}: ${String(a.value)}${a.disputed ? ' (disputed)' : ''}`} tone={a.disputed ? 'warn' : a.source === 'owner_verified' ? 'ok' : undefined} />
        ))}
      </ChipRow>
      <P small muted>Green = confirmed by the owner. Distances to station, schools and auto stands are calculated from the map.</P>
    </Screen>
  );
}
