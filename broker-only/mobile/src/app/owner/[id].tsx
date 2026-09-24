// The owner's flat: status, who handles it (the owner's tick decides), photos & videos, preferred terms.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { Image, Linking, Pressable, Text, View } from 'react-native';

import type { OwnerBroker, OwnerFlat, TxnType, UploadFile } from '@/api';
import { useSession } from '@/auth/session';
import { bhk } from '@/lib/format';
import { canUseCamera, pickFromGallery, takePhoto } from '@/lib/pickMedia';
import { Button, Card, Chip, Choice, ErrorBox, Field, H1, H2, Loading, Notice, P, Row, Screen, Tick } from '@/ui/components';
import { usePalette } from '@/ui/theme';

export default function OwnerFlatScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['owner-flat', id], queryFn: () => api.ownerFlat(id) });
  const set = (f: OwnerFlat) => {
    qc.setQueryData(['owner-flat', id], f);
    qc.invalidateQueries({ queryKey: ['owner-flats'] });
  };

  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (!q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const f = q.data;
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <H1>{f.society}</H1>
      <P muted>{f.building} · Flat {f.unit_no} · {bhk(f.bhk)} · {f.locality}</P>

      <H2>Status</H2>
      <Row style={{ flexWrap: 'wrap' }}>
        {f.statuses.length ? f.statuses.map((s) => <Chip key={s.txn_type} label={s.label} tone={s.state === 'AVAILABLE' ? 'ok' : 'info'} />) : <Chip label="Not listed by any broker yet" />}
      </Row>

      <H2>Brokers handling your flat</H2>
      {f.brokers.length === 0 ? <Notice>No broker is handling your flat yet. Find brokers near you below.</Notice> : null}
      {f.brokers.map((b) => <BrokerRow key={b.org_id} flatId={id} b={b} onChange={set} />)}
      {f.invites?.map((i) => <Notice key={i.id}>Invitation sent to {i.name} — waiting for them to accept.</Notice>)}
      <Button kind="secondary" title="Find brokers near my flat" onPress={() => router.push({ pathname: '/owner/brokers', params: { id } })} testID="find-brokers" />

      <Media flat={f} onChange={() => q.refetch()} />
      <Terms flat={f} onSaved={set} />
    </Screen>
  );
}

function BrokerRow({ flatId, b, onChange }: { flatId: string; b: OwnerBroker; onChange: (f: OwnerFlat) => void }) {
  const { api } = useSession();
  const c = usePalette();
  const [confirming, setConfirming] = useState(false);
  const [reason, setReason] = useState('');
  const [reviewing, setReviewing] = useState(false);
  const [stars, setStars] = useState(0);
  const [text, setText] = useState('');
  const allow = useMutation({
    mutationFn: (allowed: boolean) => api.setBrokerAllowed(flatId, b.org_id, allowed, allowed ? undefined : reason),
    onSuccess: (f) => { setConfirming(false); onChange(f); },
  });
  const review = useMutation({ mutationFn: () => api.reviewBroker(flatId, b.org_id, stars, text), onSuccess: () => setReviewing(false) });

  return (
    <Card>
      <Row style={{ justifyContent: 'space-between' }}>
        <P style={{ fontWeight: '700', flexShrink: 1 }}>{b.name}</P>
        {b.owner_appointed ? <Chip label="Appointed by you" tone="ok" /> : null}
      </Row>
      <P small muted>
        {b.rating_count ? `★ ${b.rating.toFixed(1)} (${b.rating_count}) · ` : ''}since {new Date(b.since).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
      </P>
      {b.contact ? (
        <Row>
          <Text selectable style={{ color: c.text, fontSize: 16, fontWeight: '600', flexShrink: 1 }}>{b.contact}</Text>
          <Button small kind="ghost" title="Call" onPress={() => Linking.openURL(`tel:${b.contact.replace(/\s/g, '')}`)} />
        </Row>
      ) : null}
      {!b.allowed ? <Notice tone="warn">Removed by you — {b.name} can’t handle your flat unless you tick the box again.</Notice> : null}
      {b.asked_back ? <Notice tone="warn">{b.name} asks to be added back: “{b.asked_back}”</Notice> : null}
      <Tick
        label="Allowed to handle my property"
        checked={b.allowed}
        onChange={(v) => (v ? allow.mutate(true) : setConfirming(true))}
        testID={`allow-${b.name}`}
      />
      {confirming ? (
        <Card style={{ borderWidth: 2 }}>
          <P>Remove {b.name}? They lose your flat and can’t add it again unless you allow them.</P>
          <Field label="Reason (optional, they will see it)" value={reason} onChangeText={setReason} />
          <Row>
            <Button small kind="danger" title="Remove" onPress={() => allow.mutate(false)} busy={allow.isPending} testID="confirm-remove" />
            <Button small kind="ghost" title="Keep" onPress={() => setConfirming(false)} />
          </Row>
        </Card>
      ) : null}
      {reviewing ? (
        <>
          <Row>{[1, 2, 3, 4, 5].map((n) => <Button key={n} small kind={n <= stars ? 'primary' : 'secondary'} title={`${n}★`} onPress={() => setStars(n)} />)}</Row>
          <Field label="What was it like? (optional)" value={text} onChangeText={setText} multiline />
          <Button small title="Submit review" disabled={!stars} onPress={() => review.mutate()} busy={review.isPending} />
        </>
      ) : review.isSuccess ? <Notice tone="ok">Thanks — your review is published.</Notice> : (
        <Button small kind="ghost" title="Review this broker" onPress={() => setReviewing(true)} />
      )}
      {allow.error || review.error ? <ErrorBox error={allow.error ?? review.error} /> : null}
    </Card>
  );
}

function Media({ flat, onChange }: { flat: OwnerFlat; onChange: () => void }) {
  const { api } = useSession();
  const c = usePalette();
  const [busy, setBusy] = useState('');
  const [error, setError] = useState<unknown>(null);
  const upload = async (get: () => Promise<UploadFile[]>) => {
    setError(null);
    try {
      const files = await get();
      for (let i = 0; i < files.length; i++) {
        setBusy(`Uploading ${i + 1} of ${files.length}…`);
        await api.uploadMedia(flat.id, files[i]);
      }
      if (files.length) onChange();
    } catch (e) {
      setError(e);
    } finally {
      setBusy('');
    }
  };
  const remove = useMutation({ mutationFn: (mid: string) => api.deleteMedia(mid), onSuccess: onChange });
  const media = flat.media ?? [];
  return (
    <>
      <H2>Photos & videos</H2>
      <P small muted>Shown to brokers handling your flat and on the flat pages they send to customers. Flat numbers are never shown to customers.</P>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
        {media.map((m) => (
          <View key={m.id} style={{ width: 104, gap: 4 }}>
            <Pressable onPress={() => Linking.openURL(m.url)} accessibilityLabel={m.kind === 'video' ? 'Play video' : 'Open photo'}>
              {m.kind === 'photo' ? (
                <Image source={{ uri: m.thumb_url }} style={{ width: 104, height: 104, borderRadius: 8, backgroundColor: c.border }} />
              ) : (
                <View style={{ width: 104, height: 104, borderRadius: 8, backgroundColor: c.brand, alignItems: 'center', justifyContent: 'center' }}>
                  <Text style={{ color: c.brandText, fontSize: 28 }}>▶</Text>
                  <Text style={{ color: c.brandText, fontSize: 12 }}>Video</Text>
                </View>
              )}
            </Pressable>
            <Button small kind="ghost" title="Remove" onPress={() => remove.mutate(m.id)} />
          </View>
        ))}
      </View>
      {media.length === 0 ? <Notice>Good photos get more serious enquiries: living room, kitchen, bedrooms, bathrooms and the view.</Notice> : null}
      {busy ? <Notice>{busy}</Notice> : (
        <Row style={{ flexWrap: 'wrap' }}>
          <Button small kind="secondary" title="Add photos" onPress={() => upload(() => pickFromGallery('photo', true))} testID="add-photos" />
          {canUseCamera ? <Button small kind="secondary" title="Take photo" onPress={() => upload(takePhoto)} /> : null}
          <Button small kind="secondary" title="Add video walkthrough" onPress={() => upload(() => pickFromGallery('video'))} />
        </Row>
      )}
      {error || remove.error ? <ErrorBox error={error ?? remove.error} /> : null}
    </>
  );
}

function Terms({ flat, onSaved }: { flat: OwnerFlat; onSaved: (f: OwnerFlat) => void }) {
  const { api } = useSession();
  const t = flat.terms;
  const [txn, setTxn] = useState<TxnType>(t.txn_type ?? 'RENT');
  const [amount, setAmount] = useState(String((txn === 'RENT' ? t.expected_rent : t.expected_price) ?? ''));
  const [deposit, setDeposit] = useState(String(t.deposit ?? ''));
  const [from, setFrom] = useState(t.available_from ?? '');
  const [pets, setPets] = useState<string | undefined>();
  const [nonveg, setNonveg] = useState<string | undefined>();
  const [bachelors, setBachelors] = useState<string | undefined>();
  const current = JSON.stringify([txn, amount, deposit, from, pets, nonveg, bachelors]);
  const [savedAs, setSavedAs] = useState(''); // "Saved" shows until anything changes again
  const num = (s: string) => (s.replace(/[^\d]/g, '') ? Number(s.replace(/[^\d]/g, '')) : undefined);
  const save = useMutation({
    mutationFn: () =>
      api.setOwnerTerms(
        flat.id,
        { txn_type: txn, ...(txn === 'RENT' ? { expected_rent: num(amount) } : { expected_price: num(amount) }), deposit: num(deposit), available_from: from || undefined },
        { ...(pets ? { pets_allowed: pets } : {}), ...(nonveg ? { nonveg_cooking: nonveg } : {}), ...(bachelors ? { bachelors_allowed: bachelors } : {}) },
      ),
    onSuccess: (f) => { onSaved(f); setSavedAs(current); },
  });
  return (
    <>
      <H2>What you’re looking for</H2>
      <P small muted>Brokers you invite receive these terms. Your house-rule answers override anything a broker enters.</P>
      <Choice label="For" value={txn} onChange={setTxn} options={[{ value: 'RENT', label: 'Rent' }, { value: 'SALE_RESALE', label: 'Sale' }]} />
      <Field label={txn === 'RENT' ? 'Expected rent per month (₹)' : 'Expected price (₹)'} keyboardType="number-pad" value={amount} onChangeText={setAmount} />
      {txn === 'RENT' ? <Field label="Deposit (₹)" keyboardType="number-pad" value={deposit} onChangeText={setDeposit} /> : null}
      <Field label="Available from" placeholder="YYYY-MM-DD, e.g. 2026-11-01" value={from} onChangeText={setFrom} />
      {txn === 'RENT' ? (
        <>
          <Choice label="Pets" value={pets} onChange={setPets} options={['no', 'cats only', 'small dogs', 'all pets', 'case-by-case'].map((v) => ({ value: v, label: v }))} />
          <Choice label="Non-veg cooking" value={nonveg} onChange={setNonveg} options={[{ value: 'allowed', label: 'Allowed' }, { value: 'not allowed', label: 'Not allowed' }]} />
          <Choice label="Bachelors" value={bachelors} onChange={setBachelors} options={[{ value: 'allowed', label: 'Allowed' }, { value: 'not allowed', label: 'Not allowed' }]} />
        </>
      ) : null}
      {save.error ? <ErrorBox error={save.error} /> : null}
      {savedAs === current ? <Notice tone="ok">Saved.</Notice> : null}
      <Button title="Save" onPress={() => save.mutate()} busy={save.isPending} />
    </>
  );
}
