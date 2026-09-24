// D16: one message to many of the broker's own customers — a new flat, a price drop, or news.
// Delivered in the app; customers not on the app yet are listed with a WhatsApp invite.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { Linking } from 'react-native';

import type { BroadcastKind, Listing } from '@/api';
import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Choice, ErrorBox, Field, H2, Notice, P, Row, Screen } from '@/ui/components';
import { FlatSearch } from '@/ui/FlatSearch';

const KINDS: { value: BroadcastKind; label: string }[] = [
  { value: 'new_flat', label: 'New flat' },
  { value: 'price_drop', label: 'Price drop in an area' },
  { value: 'news', label: 'News' },
];

export default function BroadcastScreen() {
  const { api } = useSession();
  const qc = useQueryClient();
  const [kind, setKind] = useState<BroadcastKind>('new_flat');
  const [flat, setFlat] = useState<Listing | null>(null);
  const [localityId, setLocalityId] = useState<string | undefined>();
  const [scope, setScope] = useState<'all' | 'locality'>('all');
  const [text, setText] = useState<string | null>(null); // null = use the suggested text
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities });
  const input = {
    kind,
    listing_id: kind === 'new_flat' ? flat?.id : undefined,
    locality_id: localityId,
    scope: localityId ? scope : 'all',
  } as const;
  const preview = useQuery({ queryKey: ['bc-preview', input], queryFn: () => api.broadcastPreview(input) });
  const history = useQuery({ queryKey: ['broadcasts'], queryFn: api.broadcasts });
  const message = text ?? preview.data?.text ?? '';
  const send = useMutation({
    mutationFn: () => api.sendBroadcast({ ...input, text: message }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['broadcasts'] }),
  });
  const reach = preview.data?.reach;
  const ready = message.trim().length > 0 && (kind !== 'new_flat' || flat);

  if (send.data) {
    const r = send.data;
    return (
      <Screen>
        <Notice tone="ok">Sent in the app to {r.delivered_in_app} customer{r.delivered_in_app === 1 ? '' : 's'}.{r.muted ? ` ${r.muted} turned your updates off.` : ''}</Notice>
        {r.invite.length ? (
          <>
            <H2>{r.not_on_app} not on the app yet</H2>
            <P small muted>Tap to send them this update on WhatsApp with an invite to the app. Once they join, your next update reaches them automatically.</P>
            {r.invite.map((c) => (
              <Card key={c.customer_id}>
                <Row style={{ justifyContent: 'space-between' }}>
                  <P style={{ fontWeight: '600', flexShrink: 1 }}>{c.name}</P>
                  <Button small kind="secondary" title="WhatsApp invite" onPress={() => Linking.openURL(c.whatsapp_url)} />
                </Row>
              </Card>
            ))}
          </>
        ) : null}
        <Button kind="ghost" title="Send another update" onPress={() => { send.reset(); setText(null); setFlat(null); }} />
      </Screen>
    );
  }

  return (
    <Screen>
      <P muted>Reaches your own customers only — never another broker’s. Free during the pilot.</P>
      <Choice label="What’s the news?" value={kind} onChange={(k) => { setKind(k); setText(null); }} options={KINDS} />

      {kind === 'new_flat' ? (
        flat ? (
          <Card>
            <Row style={{ justifyContent: 'space-between' }}>
              <P style={{ fontWeight: '700', flexShrink: 1 }}>{flat.society}</P>
              <Button small kind="ghost" title="Change" onPress={() => { setFlat(null); setText(null); }} />
            </Row>
            <P small muted>{flat.building} · Flat {flat.unit_no} — customers see the society, not the flat number.</P>
          </Card>
        ) : <FlatSearch label="Which of your flats?" pickedIds={[]} onPick={(l) => { setFlat(l); setText(null); }} />
      ) : null}

      <P small style={{ fontWeight: '600' }}>{kind === 'price_drop' ? 'Area' : 'Area (optional)'}</P>
      <ChipRow>
        {localities.data?.map((l) => (
          <Chip key={l.id} label={l.name} selected={localityId === l.id} onPress={() => { setLocalityId(localityId === l.id ? undefined : l.id); setText(null); }} />
        ))}
      </ChipRow>
      {localityId ? (
        <Choice label="Send to" value={scope} onChange={setScope} options={[{ value: 'all', label: 'All my customers' }, { value: 'locality', label: 'Customers looking in this area' }]} />
      ) : null}

      <Field label="Message" value={message} onChangeText={setText} multiline maxLength={500} hint={`${message.length}/500`} testID="broadcast-text" />
      {reach ? (
        <Notice>
          {reach.total} customer{reach.total === 1 ? '' : 's'}: {reach.in_app} get it in the app{reach.not_on_app ? `, ${reach.not_on_app} not on the app yet (you can invite them after sending)` : ''}{reach.muted ? `, ${reach.muted} turned your updates off` : ''}.
        </Notice>
      ) : null}
      {send.error ? <ErrorBox error={send.error} /> : null}
      <Button title="Send update" onPress={() => send.mutate()} disabled={!ready} busy={send.isPending} testID="send-broadcast" />

      {history.data?.length ? (
        <>
          <H2>Sent</H2>
          {history.data.map((b) => (
            <Card key={b.id}>
              <P small muted>{ago(b.created_at)} · {b.delivered_in_app} in app · {b.not_on_app} not on app</P>
              <P>{b.text}</P>
            </Card>
          ))}
        </>
      ) : null}
    </Screen>
  );
}
