// D17: share ready flats (or ask for a flat a customer needs) with fellow brokers from the broker's own list.
// Audience: in and around the flat (distance widened by the broker), everyone on the list, or ticked names.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { Linking } from 'react-native';

import type { TradeInput, TradeKind, TradeScope } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Card, Chip, ChipRow, Choice, ErrorBox, Field, H2, Loading, Notice, P, Row, Screen, Tick } from '@/ui/components';
import { FlatPicker } from '@/ui/FlatPicker';

const RADII = [1, 3, 5, 10, 25];

export default function TradeBlastScreen() {
  const { api } = useSession();
  const qc = useQueryClient();
  const params = useLocalSearchParams<{ kind?: string }>();
  const [kind, setKind] = useState<TradeKind>(params.kind === 'requirement' ? 'requirement' : 'flats');
  const [flatIds, setFlatIds] = useState<string[]>([]);
  const [customerId, setCustomerId] = useState<string | undefined>();
  const [reqId, setReqId] = useState<string | undefined>();
  const [scope, setScope] = useState<TradeScope>('radius');
  const [radius, setRadius] = useState(3);
  const [ticked, setTicked] = useState<string[]>([]);
  const [text, setText] = useState<string | null>(null);

  const customers = useQuery({ queryKey: ['customers', ''], queryFn: () => api.customers(), enabled: kind === 'requirement' });
  const customer = useQuery({ queryKey: ['customer', customerId], queryFn: () => api.customer(customerId!), enabled: !!customerId });
  const input: TradeInput = {
    kind,
    listing_ids: kind === 'flats' ? flatIds : undefined,
    requirement_id: kind === 'requirement' ? reqId : undefined,
    scope,
    radius_km: radius,
    contact_ids: scope === 'selected' ? ticked : undefined,
  };
  const ready = kind === 'flats' ? flatIds.length > 0 : !!reqId;
  const preview = useQuery({ queryKey: ['trade-preview', input], queryFn: () => api.tradePreview(input), enabled: ready });
  const message = text ?? preview.data?.text ?? '';
  const send = useMutation({
    mutationFn: () => api.sendTradeBlast({ ...input, text: message }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['trade-blasts'] }),
  });
  const reach = preview.data?.reach;

  // Ticking a name switches to "pick names", starting from whoever is selected now.
  const tick = (cid: string, on: boolean) => {
    const base = scope === 'selected' ? ticked : (preview.data?.contacts ?? []).filter((c) => c.selected).map((c) => c.id);
    setScope('selected');
    setTicked(on ? [...new Set([...base, cid])] : base.filter((x) => x !== cid));
  };

  if (send.data) {
    const r = send.data;
    return (
      <Screen>
        <Notice tone="ok">Sent to {r.recipients_total} fellow broker{r.recipients_total === 1 ? '' : 's'}: {r.delivered_in_app} in the app{r.via_whatsapp ? `, ${r.via_whatsapp} by WhatsApp (tap below)` : ''}.</Notice>
        {r.whatsapp.map((c) => (
          <Card key={c.contact_id}>
            <Row style={{ justifyContent: 'space-between' }}>
              <P style={{ fontWeight: '600', flexShrink: 1 }}>{c.name}{c.firm && c.firm !== c.name ? ` · ${c.firm}` : ''}</P>
              <Button small kind="secondary" title="WhatsApp" onPress={() => Linking.openURL(c.whatsapp_url)} />
            </Row>
          </Card>
        ))}
        <Button title="See replies" onPress={() => router.replace(`/trade/${r.id}`)} />
        <Button kind="ghost" title="Send another" onPress={() => { send.reset(); setText(null); setFlatIds([]); setReqId(undefined); }} />
      </Screen>
    );
  }

  return (
    <Screen>
      <Choice label="What do you want to send?" value={kind} onChange={(k) => { setKind(k); setText(null); }} options={[{ value: 'flats', label: 'My ready flats' }, { value: 'requirement', label: 'A customer’s requirement' }]} />

      {kind === 'flats' ? (
        <FlatPicker picked={flatIds} onChange={(ids) => { setFlatIds(ids); setText(null); }} label="Which of your flats? Pick one or several" />
      ) : (
        <>
          <P small style={{ fontWeight: '600' }}>Which customer?</P>
          {customers.isLoading ? <Loading /> : null}
          <ChipRow>
            {customers.data?.slice(0, 30).map((c) => (
              <Chip key={c.id} label={c.name || c.phone} selected={customerId === c.id} onPress={() => { setCustomerId(c.id); setReqId(undefined); setText(null); }} />
            ))}
          </ChipRow>
          {customer.data ? (
            customer.data.requirements?.length ? (
              <Choice label="Requirement" value={reqId} onChange={(v) => { setReqId(v); setText(null); }} options={(customer.data.requirements ?? []).map((r) => ({ value: r.id, label: r.summary }))} />
            ) : <Notice>Add a requirement for this customer first.</Notice>
          ) : null}
          <P small muted>Fellow brokers see what is wanted — never your customer’s name or number.</P>
        </>
      )}

      {ready ? (
        <>
          <H2>Who gets it</H2>
          <Choice
            value={scope}
            onChange={(v) => setScope(v)}
            options={[{ value: 'radius', label: 'In and around the flat' }, { value: 'all', label: 'Everyone on my list' }, { value: 'selected', label: 'Only names I tick' }]}
          />
          {scope === 'radius' ? (
            <ChipRow>
              {RADII.map((k) => <Chip key={k} label={`${k} km`} selected={radius === k} onPress={() => setRadius(k)} />)}
            </ChipRow>
          ) : null}
          {preview.isLoading ? <Loading /> : preview.error ? <ErrorBox error={preview.error} /> : null}
          {reach ? (
            <Notice tone={reach.selected ? 'info' : 'warn'}>
              {reach.selected} of {reach.total} fellow brokers selected: {reach.in_app} get it in the app, {reach.whatsapp} by WhatsApp.
              {reach.no_location ? ` ${reach.no_location} have no area on record, so they are only reached with “Everyone” or a tick.` : ''}
            </Notice>
          ) : null}
          {preview.data?.contacts.map((c) => (
            <Card key={c.id}>
              <Tick
                checked={!!c.selected}
                onChange={(on) => tick(c.id, on)}
                label={`${c.name}${c.firm && c.firm !== c.name ? ` · ${c.firm}` : ''} — ${c.distance_km !== null ? `${c.distance_km} km` : 'area not known'}${c.locality ? ` (${c.locality})` : ''}${c.on_platform ? ' · on app' : ''}`}
                testID={`fellow-${c.id}`}
              />
            </Card>
          ))}
          {preview.data && !preview.data.contacts.length ? (
            <Notice tone="warn">Your list of fellow brokers is empty. Add them first.</Notice>
          ) : null}
          <Button kind="ghost" title="Add or import fellow brokers" onPress={() => router.push('/trade/contacts')} />

          <Field label="Message" value={message} onChangeText={setText} multiline maxLength={1000} hint={`${message.length}/1000 · no commission terms are added`} testID="trade-text" />
          {send.error ? <ErrorBox error={send.error} /> : null}
          <Button title="Send to fellow brokers" onPress={() => send.mutate()} disabled={!reach?.selected || !message.trim()} busy={send.isPending} testID="send-trade" />
        </>
      ) : null}
    </Screen>
  );
}
