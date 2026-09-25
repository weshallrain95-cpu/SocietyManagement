// "Add flat" — the docs/06 flow: ~10 taps for a known society. House rules default to "Ask owner".
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';
import { View } from 'react-native';

import { ApiError, type FlatCheck, type SocietyCandidate, type TxnType } from '@/api';
import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { useDebounced } from '@/lib/useDebounced';
import { Button, Card, Chip, ChipRow, Choice, ErrorBox, Field, H2, Notice, P, Row, Screen } from '@/ui/components';

const BHK = ['0.5', '1', '1.5', '2', '2.5', '3', '4'];
const bhkLabel = (b: string) => (b === '0.5' ? '1 RK' : `${b} BHK`);

export default function AddFlat() {
  const { api } = useSession();
  const qc = useQueryClient();
  const [q, setQ] = useState('');
  const [society, setSociety] = useState<SocietyCandidate | null>(null);
  const [wing, setWing] = useState('');
  const [unitNo, setUnitNo] = useState('');
  const [bhk, setBhk] = useState('2');
  const [txn, setTxn] = useState<TxnType>('RENT');
  const [price, setPrice] = useState('');
  const [deposit, setDeposit] = useState('');
  const [furnishing, setFurnishing] = useState('semi-furnished');
  const [parking, setParking] = useState('0');
  const [keys, setKeys] = useState('office');
  const [ownerPhone, setOwnerPhone] = useState('');
  const [askOwner, setAskOwner] = useState(true);
  const [availableNow, setAvailableNow] = useState(true);
  const [pets, setPets] = useState<string | undefined>();
  const [nonveg, setNonveg] = useState<string | undefined>();
  const [bachelors, setBachelors] = useState<string | undefined>();

  const [otherWing, setOtherWing] = useState(false);
  const [reported, setReported] = useState('');
  const sid = society?.society_id;
  const wingsQ = useQuery({ queryKey: ['wings', sid], queryFn: () => api.wings(sid!), enabled: !!sid });
  const wings = wingsQ.data?.wings ?? [];
  // Check the flat while the broker types (after a short pause), so mistakes show before saving.
  const typed = useDebounced(`${wing}|${unitNo.trim()}`, 400);
  const check = useQuery({
    queryKey: ['check-flat', sid, typed],
    queryFn: () => api.checkFlat(sid!, { wing: typed.split('|')[0] || undefined, unit_no: typed.split('|')[1] }),
    enabled: !!sid && !!typed.split('|')[1],
  });

  const search = useQuery({ queryKey: ['soc', q], queryFn: () => api.searchSocieties(q), enabled: q.trim().length >= 2 && !society });
  const rent = txn === 'RENT';
  const amount = Number(price.replace(/[^\d]/g, ''));

  const save = useMutation({
    mutationFn: (confirm_layout: boolean) =>
      api.createListing({
        confirm_layout,
        society_id: society!.society_id,
        building: wing || undefined,
        unit_no: unitNo.trim(),
        bhk,
        txn_type: txn,
        ...(rent ? { asking_rent: amount } : { asking_price: amount }),
        deposit: deposit ? Number(deposit.replace(/[^\d]/g, '')) : rent ? amount * 3 : undefined,
        owner_phone: indianMobile(ownerPhone) ?? undefined,
        keys: { holder_type: keys },
        available_now: availableNow,
        attributes: {
          furnishing,
          car_parking_covered: Number(parking),
          ...(!askOwner && pets ? { pets_allowed: pets } : {}),
          ...(!askOwner && nonveg ? { nonveg_cooking: nonveg } : {}),
          ...(!askOwner && bachelors ? { bachelors_allowed: bachelors } : {}),
        },
      }),
    onSuccess: (l) => {
      qc.invalidateQueries({ queryKey: ['listings'] });
      qc.invalidateQueries({ queryKey: ['flat-search'] });
      router.replace(`/listing/${l.id}`);
    },
  });

  // A 409/422 from the server carries the same check; prefer it (it is what refused the save).
  const refused = save.error instanceof ApiError && [409, 422].includes(save.error.status)
    ? ((save.error.body as { layout?: FlatCheck })?.layout ?? null) : null;
  const flat = refused ?? check.data ?? null;
  const report = useMutation({
    mutationFn: () => api.reportLayout(flat!.building!.id, { unit_no: unitNo.trim() }),
    onSuccess: (r) => setReported(r.detail),
  });
  const ready = society && unitNo.trim() && amount > 0 && !flat?.blocking;
  const pickWing = (w: string) => {
    setWing(w);
    setOtherWing(false);
    save.reset();
  };

  return (
    <Screen>
      <H2>1 · Society</H2>
      {society ? (
        <Card>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{society.name}</P>
            <Button small kind="ghost" title="Change" onPress={() => { setSociety(null); setWing(""); setOtherWing(false); save.reset(); }} />
          </Row>
          <P muted small>{society.locality}{society.status === 'provisional' ? ' · awaiting approval' : ''}</P>
        </Card>
      ) : (
        <>
          <Field label="Search society" placeholder="e.g. Hiranandani Estate" value={q} onChangeText={setQ} autoCorrect={false} testID="society-search" hint="Spelling mistakes and short forms are fine." />
          {search.data?.map((s) => (
            <Card key={s.society_id} onPress={() => setSociety(s)}>
              <P style={{ fontWeight: '600' }}>{s.name}</P>
              <P muted small>{s.locality}</P>
            </Card>
          ))}
          {search.data?.length === 0 ? <Notice tone="warn">Not found. Propose a new society from the desktop console; ops will verify it.</Notice> : null}
        </>
      )}

      <H2>2 · Flat</H2>
      {wings.length > 0 && !otherWing ? (
        <View style={{ gap: 6 }}>
          <P small muted>Wing / building</P>
          <ChipRow>
            {wings.map((w) => <Chip key={w.id} label={w.name} selected={wing === w.name} onPress={() => pickWing(w.name)} />)}
            {!wingsQ.data?.wings_complete ? <Chip label="Other…" onPress={() => { setOtherWing(true); setWing(''); }} /> : null}
          </ChipRow>
        </View>
      ) : null}
      <Row>
        {wings.length === 0 || otherWing ? (
          <Half><Field label="Wing / building" placeholder="A" value={wing} onChangeText={(v) => { setWing(v); save.reset(); }} autoCapitalize="characters" /></Half>
        ) : null}
        <Half><Field label="Flat number" placeholder="1203" value={unitNo} onChangeText={(v) => { setUnitNo(v); save.reset(); setReported(''); }} keyboardType="default" testID="unit-no" /></Half>
      </Row>
      {flat?.building?.layout.floors_total && flat.building.layout.units_per_floor ? (
        <P small muted>
          {flat.building.name}: {flat.building.layout.floors_total} floors, {flat.building.layout.units_per_floor} flats per floor
          {flat.building.layout.verified ? ' · verified' : ''}
        </P>
      ) : null}
      {flat?.issues.map((i) => (
        <Notice key={i.code} tone={i.blocking ? 'bad' : 'warn'}>{i.message}</Notice>
      ))}
      {flat?.suggestions.length && !flat.building ? (
        <ChipRow>{flat.suggestions.map((w) => <Chip key={w} label={w} tone="info" onPress={() => pickWing(w)} />)}</ChipRow>
      ) : null}
      {flat?.blocking && flat.building && unitNo.trim() ? (
        reported ? <Notice tone="ok">{reported}</Notice> : (
          <Button small kind="ghost" title="This flat really exists — tell Only Broker" onPress={() => report.mutate()} busy={report.isPending} />
        )
      ) : null}
      <Choice label="Configuration" value={bhk} onChange={setBhk} options={BHK.map((b) => ({ value: b, label: bhkLabel(b) }))} />
      <Choice label="For" value={txn} onChange={setTxn} options={[{ value: 'RENT', label: 'Rent' }, { value: 'SALE_RESALE', label: 'Resale' }, { value: 'SALE_NEW', label: 'New sale' }]} />
      <Choice label="Furnishing" value={furnishing} onChange={setFurnishing} options={[{ value: 'unfurnished', label: 'Unfurnished' }, { value: 'semi-furnished', label: 'Semi' }, { value: 'fully furnished', label: 'Full' }]} />
      <Choice label="Covered parking" value={parking} onChange={setParking} options={['0', '1', '2', '3'].map((p) => ({ value: p, label: p === '0' ? 'None' : p }))} />

      <H2>3 · Price</H2>
      <Field label={rent ? 'Rent per month (₹)' : 'Expected price (₹)'} keyboardType="number-pad" value={price} onChangeText={setPrice} testID="price" />
      {rent ? <Field label="Deposit (₹)" keyboardType="number-pad" value={deposit} onChangeText={setDeposit} placeholder={amount ? String(amount * 3) : '3 months by default'} /> : null}

      <H2>4 · Keys & owner</H2>
      <Choice label="Keys are with" value={keys} onChange={setKeys} options={[{ value: 'office', label: 'My office' }, { value: 'owner', label: 'Owner' }, { value: 'society_office', label: 'Society office' }, { value: 'lockbox', label: 'Lock-box' }]} />
      <Field label="Owner mobile (private to you)" keyboardType="phone-pad" value={ownerPhone} onChangeText={setOwnerPhone} hint="Used to send the owner visit notices and availability checks." />

      <H2>5 · House rules</H2>
      <ChipRow>
        <Chip label="Ask owner (recommended)" selected={askOwner} onPress={() => setAskOwner(true)} />
        <Chip label="I know them" selected={!askOwner} onPress={() => setAskOwner(false)} />
      </ChipRow>
      {askOwner ? (
        <Notice>The owner gets a WhatsApp link with at most 10 one-tap questions. Owner answers override broker answers.</Notice>
      ) : (
        <>
          <Choice label="Pets" value={pets} onChange={setPets} options={['no', 'cats only', 'small dogs', 'all pets', 'case-by-case'].map((v) => ({ value: v, label: v }))} />
          <Choice label="Non-veg cooking" value={nonveg} onChange={setNonveg} options={[{ value: 'allowed', label: 'Allowed' }, { value: 'not allowed', label: 'Not allowed' }]} />
          <Choice label="Bachelors" value={bachelors} onChange={setBachelors} options={[{ value: 'allowed', label: 'Allowed' }, { value: 'not allowed', label: 'Not allowed' }]} />
        </>
      )}

      <H2>6 · Offer it now?</H2>
      <ChipRow>
        <Chip label="Yes — Available now" selected={availableNow} onPress={() => setAvailableNow(true)} />
        <Chip label="Not yet — All flats only" selected={!availableNow} onPress={() => setAvailableNow(false)} />
      </ChipRow>
      <P small muted>{availableNow ? 'It goes into your Available now list: matched to customers and ready to share.' : 'It is saved in All flats. Make it available from there whenever you like.'}</P>

      {save.error && !refused ? <ErrorBox error={save.error} /> : null}
      {refused && !refused.blocking ? (
        <Button title="Number is right — save anyway" kind="ghost" onPress={() => save.mutate(true)} busy={save.isPending} testID="save-anyway" />
      ) : null}
      <Button title="Save flat" onPress={() => save.mutate(false)} disabled={!ready} busy={save.isPending} testID="save-flat" />
      <P small muted>New flats show as “not yet confirmed by owner” until the owner says YES.</P>
    </Screen>
  );
}

function Half({ children }: { children: React.ReactNode }) {
  return <View style={{ flex: 1 }}>{children}</View>;
}
