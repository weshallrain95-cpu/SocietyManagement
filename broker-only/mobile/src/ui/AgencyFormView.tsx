// The broker's business form (founder decision 2026-09-25): first-time registration, and later the Admin's
// "Agency details". Sections mirror what ops checks: who the business is, who owns it, its registrations,
// its office, the work it does, and a declaration.
import { useQuery } from '@tanstack/react-query';
import React, { useState } from 'react';
import { Pressable, Text, View } from 'react-native';

import type { AgencyForm, AgencyProfile, OwnershipType, TxnType } from '@/api';
import { ApiError } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Chip, ChipRow, ErrorBox, Field, H2, Notice, P } from './components';
import { usePalette } from './theme';

const OWNERSHIP: { value: OwnershipType; label: string; owner: string; pan: string; min: number; max?: number }[] = [
  { value: 'proprietorship', label: 'Proprietorship', owner: 'Proprietor', pan: 'your own PAN (4th letter P)', min: 1, max: 1 },
  { value: 'individual', label: 'Individual (no firm)', owner: 'Owner', pan: 'your own PAN (4th letter P)', min: 1, max: 1 },
  { value: 'partnership', label: 'Partnership firm', owner: 'Partner', pan: "the firm's PAN (4th letter F)", min: 2 },
  { value: 'llp', label: 'LLP', owner: 'Designated partner', pan: "the LLP's PAN (4th letter F)", min: 2 },
  { value: 'private_limited', label: 'Private limited', owner: 'Director', pan: "the company's PAN (4th letter C)", min: 1 },
  { value: 'public_limited', label: 'Public limited', owner: 'Director', pan: "the company's PAN (4th letter C)", min: 1 },
];
const TXNS: { value: TxnType; label: string }[] = [
  { value: 'RENT', label: 'Rentals' }, { value: 'SALE_RESALE', label: 'Resale' }, { value: 'SALE_NEW', label: 'New projects' },
];
const PAN = /^[A-Z]{3}[ABCFGHLJPT][A-Z]\d{4}[A-Z]$/;
const GSTIN = /^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;
const up = (s: string) => s.replace(/[\s-]/g, '').toUpperCase();

export function AgencyFormView({ initial, mode, busy, error, onSubmit }: {
  initial?: AgencyProfile;
  mode: 'register' | 'edit';
  busy: boolean;
  error: unknown;
  onSubmit: (form: AgencyForm) => void;
}) {
  const { api } = useSession();
  const c = usePalette();
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities });
  const [name, setName] = useState(initial?.name ?? '');
  const [legal, setLegal] = useState(initial?.legal_name ?? '');
  const [own, setOwn] = useState<OwnershipType | undefined>(initial?.ownership_type);
  const [owners, setOwners] = useState<string[]>(initial?.owners.map((o) => o.name) ?? ['']);
  const [year, setYear] = useState(initial?.established_year ? String(initial.established_year) : '');
  const [pan, setPan] = useState('');
  const [gst, setGst] = useState(initial?.gst_registered ?? false);
  const [gstin, setGstin] = useState(initial?.gstin ?? '');
  const [reg, setReg] = useState(initial?.company_reg_no ?? '');
  const [rera, setRera] = useState(initial?.rera_agent_no ?? '');
  const [email, setEmail] = useState(initial?.contact_email ?? '');
  const [addr1, setAddr1] = useState(initial?.office_address ?? '');
  const [addr2, setAddr2] = useState(initial?.office_address_2 ?? '');
  const [loc, setLoc] = useState<string | undefined>(initial?.office_locality);
  const [city, setCity] = useState(initial?.office_city || 'Thane');
  const [pin, setPin] = useState(initial?.office_pincode ?? '');
  const [txns, setTxns] = useState<TxnType[]>(initial?.txn_types ?? ['RENT']);
  const [serves, setServes] = useState<string[]>([]);
  const [agree, setAgree] = useState(false);

  const kind = OWNERSHIP.find((o) => o.value === own);
  const server = error instanceof ApiError && error.body && typeof error.body === 'object' ? (error.body as Record<string, unknown>) : {};
  const fe = (k: string) => {
    const v = server[k];
    return Array.isArray(v) ? String(v[0]) : typeof v === 'string' ? v : undefined;
  };
  const panC = up(pan);
  const gstC = up(gstin);
  const reraC = up(rera);
  const soloOwner = own === 'proprietorship' || own === 'individual';
  const ownerList = soloOwner ? owners.slice(0, 1) : owners;
  const problems = {
    pan: panC && !PAN.test(panC) ? 'PAN looks like ABCDE1234F' : undefined,
    gstin: gst && gstC && !GSTIN.test(gstC) ? 'GSTIN is 15 characters, like 27ABCDE1234F1Z5' : gst && gstC && panC && gstC.slice(2, 12) !== panC ? 'The GSTIN should contain the PAN above' : undefined,
    rera: txns.includes('SALE_NEW') && !reraC ? 'Needed to sell new projects' : reraC && !/^A\d{11}$/.test(reraC) ? 'Looks like A51700012345' : undefined,
    pin: pin && !/^[1-9]\d{5}$/.test(pin) ? '6 digits' : undefined,
  };
  const ready =
    name.trim().length >= 3 && legal.trim().length >= 3 && !!own && ownerList.filter((o) => o.trim().length >= 3).length >= (kind?.min ?? 1) &&
    (mode === 'edit' || PAN.test(panC)) && (!gst || GSTIN.test(gstC)) && !problems.rera && addr1.trim().length >= 5 && !!loc &&
    /^[1-9]\d{5}$/.test(pin) && txns.length > 0 && (mode === 'edit' || (serves.length > 0 && agree));

  const submit = () =>
    onSubmit({
      name: name.trim(), legal_name: legal.trim(), ownership_type: own!, owners: ownerList.filter((o) => o.trim()).map((o) => ({ name: o.trim() })),
      established_year: year ? Number(year) : null, ...(panC ? { pan: panC } : {}), gst_registered: gst, gstin: gst ? gstC : '',
      company_reg_no: reg.trim(), rera_agent_no: reraC, contact_email: email.trim(), office_address: addr1.trim(), office_address_2: addr2.trim(),
      office_locality: loc!, office_city: city.trim() || 'Thane', office_pincode: pin, txn_types: txns,
      ...(mode === 'register' ? { service_locality_ids: serves, declaration: agree } : {}),
    });

  return (
    <>
      {mode === 'register' ? (
        <Notice>Welcome to Only Broker. Tell us about your business once; ops verifies it within a working day, and you can add flats and customers straight away.</Notice>
      ) : null}

      <H2>1 · Your business</H2>
      <Field label="Agency name (what customers see)" value={name} onChangeText={setName} placeholder="Shah Realty" error={fe('name')} testID="agency-name" />
      <P small style={{ fontWeight: '600' }}>Type of business</P>
      <ChipRow>
        {OWNERSHIP.map((o) => <Chip key={o.value} label={o.label} selected={own === o.value} onPress={() => setOwn(o.value)} />)}
      </ChipRow>
      {fe('ownership_type') ? <P small style={{ color: c.bad }}>{fe('ownership_type')}</P> : null}
      <Field
        label={soloOwner ? 'Your full name as on PAN' : 'Legal name as on PAN / GST'}
        value={legal}
        onChangeText={setLegal}
        placeholder={soloOwner ? 'Ravi Mahesh Shah' : 'Shah Realty LLP'}
        error={fe('legal_name')}
        testID="legal-name"
      />
      <Field label="Year started (optional)" keyboardType="number-pad" maxLength={4} value={year} onChangeText={setYear} error={fe('established_year')} />

      {own ? (
        <>
          <H2>2 · {soloOwner ? kind!.owner : `${kind!.owner}s`}</H2>
          {ownerList.map((o, i) => (
            <View key={i} style={{ gap: 4 }}>
              <Field
                label={soloOwner ? `${kind!.owner}'s full name` : `${kind!.owner} ${i + 1} — full name`}
                value={o}
                onChangeText={(t) => setOwners(ownerList.map((x, j) => (j === i ? t : x)))}
                testID={`owner-${i}`}
              />
              {!soloOwner && ownerList.length > (kind?.min ?? 1) ? (
                <Button small kind="ghost" title="Remove" onPress={() => setOwners(ownerList.filter((_, j) => j !== i))} />
              ) : null}
            </View>
          ))}
          {!soloOwner ? <Button small kind="secondary" title={`+ Add ${kind!.owner.toLowerCase()}`} onPress={() => setOwners([...ownerList, ''])} /> : null}
          {fe('owners') ? <P small style={{ color: c.bad }}>{fe('owners')}</P> : null}
          {!soloOwner && ownerList.length < kind!.min ? <P small muted>Add at least {kind!.min} {kind!.owner.toLowerCase()}s.</P> : null}
        </>
      ) : null}

      <H2>3 · Registrations</H2>
      <Field
        label={mode === 'edit' ? `PAN (on file: ${initial?.pan_masked || '—'}) — type only to change it` : 'PAN'}
        value={pan}
        onChangeText={setPan}
        autoCapitalize="characters"
        maxLength={10}
        hint={kind ? `Use ${kind.pan}. Stored encrypted; ops sees it masked.` : 'Stored encrypted; ops sees it masked.'}
        error={problems.pan ?? fe('pan')}
        testID="pan"
      />
      <Pressable onPress={() => setGst(!gst)} accessibilityRole="checkbox" accessibilityState={{ checked: gst }} style={{ flexDirection: 'row', alignItems: 'center', gap: 10, minHeight: 40 }}>
        <View style={{ width: 22, height: 22, borderRadius: 6, borderWidth: 2, borderColor: gst ? c.brand : c.border, backgroundColor: gst ? c.brand : 'transparent', alignItems: 'center', justifyContent: 'center' }}>
          {gst ? <Text style={{ color: c.brandText, fontWeight: '800' }}>✓</Text> : null}
        </View>
        <Text style={{ color: c.text, fontSize: 15 }}>Registered for GST</Text>
      </Pressable>
      {gst ? <Field label="GSTIN" value={gstin} onChangeText={setGstin} autoCapitalize="characters" maxLength={15} error={problems.gstin ?? fe('gstin')} testID="gstin" /> : (
        <P small muted>Not needed if your turnover is under ₹20 lakh a year.</P>
      )}
      {own === 'llp' || own === 'private_limited' || own === 'public_limited' || own === 'partnership' ? (
        <Field label={own === 'llp' ? 'LLPIN (optional)' : own === 'partnership' ? 'Firm registration no. (optional)' : 'CIN (optional)'} value={reg} onChangeText={setReg} autoCapitalize="characters" error={fe('company_reg_no')} />
      ) : null}
      <Field
        label={txns.includes('SALE_NEW') ? 'MahaRERA agent number' : 'MahaRERA agent number (optional for rentals and resale)'}
        value={rera}
        onChangeText={setRera}
        autoCapitalize="characters"
        placeholder="A51700012345"
        error={problems.rera ?? fe('rera_agent_no')}
        testID="rera"
      />

      <H2>4 · Office</H2>
      <Field label="Office address" value={addr1} onChangeText={setAddr1} placeholder="Shop 3, Ground floor, Sai Plaza" error={fe('office_address')} testID="addr1" />
      <Field label="Landmark / road (optional)" value={addr2} onChangeText={setAddr2} placeholder="Near Dhokali Naka, Kolshet Road" />
      <P small style={{ fontWeight: '600' }}>Area</P>
      <ChipRow>
        {localities.data?.map((l) => (
          <Chip key={l.id} label={l.name} selected={loc === l.id} onPress={() => { setLoc(l.id); if (!serves.length) setServes([l.id]); }} />
        ))}
      </ChipRow>
      {fe('office_locality') ? <P small style={{ color: c.bad }}>{fe('office_locality')}</P> : null}
      <Field label="City" value={city} onChangeText={setCity} />
      <Field label="Pincode" keyboardType="number-pad" maxLength={6} value={pin} onChangeText={setPin} error={problems.pin ?? fe('office_pincode')} testID="pincode" />
      <Field label="Email for invoices (optional)" keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} error={fe('contact_email')} />

      <H2>5 · Your work</H2>
      <P small style={{ fontWeight: '600' }}>You handle</P>
      <ChipRow>
        {TXNS.map((t) => <Chip key={t.value} label={t.label} selected={txns.includes(t.value)} onPress={() => setTxns(txns.includes(t.value) ? txns.filter((x) => x !== t.value) : [...txns, t.value])} />)}
      </ChipRow>
      {mode === 'register' ? (
        <>
          <P small style={{ fontWeight: '600' }}>Areas you serve</P>
          <ChipRow>
            {localities.data?.map((l) => (
              <Chip key={l.id} label={l.name} selected={serves.includes(l.id)} onPress={() => setServes(serves.includes(l.id) ? serves.filter((x) => x !== l.id) : [...serves, l.id])} />
            ))}
          </ChipRow>
          <P small muted>Customers asking for flats in these areas reach you. You can change them later.</P>
          {fe('service_locality_ids') ? <P small style={{ color: c.bad }}>{fe('service_locality_ids')}</P> : null}
        </>
      ) : initial?.service_areas.length ? (
        <P small muted>Areas you serve: {initial.service_areas.map((a) => a.label).join(', ')}</P>
      ) : null}

      {mode === 'register' ? (
        <>
          <H2>6 · Declaration</H2>
          <Pressable onPress={() => setAgree(!agree)} accessibilityRole="checkbox" accessibilityState={{ checked: agree }} style={{ flexDirection: 'row', gap: 10 }} testID="declaration">
            <View style={{ width: 22, height: 22, marginTop: 2, borderRadius: 6, borderWidth: 2, borderColor: agree ? c.brand : c.border, backgroundColor: agree ? c.brand : 'transparent', alignItems: 'center', justifyContent: 'center' }}>
              {agree ? <Text style={{ color: c.brandText, fontWeight: '800' }}>✓</Text> : null}
            </View>
            <Text style={{ color: c.text, fontSize: 14, flex: 1 }}>
              I confirm these details are true and that I am authorised to register this business. Only Broker may check them against MahaRERA, GST and PAN records.
            </Text>
          </Pressable>
          {fe('declaration') ? <P small style={{ color: c.bad }}>{fe('declaration')}</P> : null}
        </>
      ) : null}

      {error && !Object.keys(server).some((k) => k !== 'detail') ? <ErrorBox error={error} /> : null}
      {error && Object.keys(server).some((k) => k !== 'detail') ? <Notice tone="warn">Please fix the highlighted fields.</Notice> : null}
      <Button title={mode === 'register' ? 'Register my agency' : 'Save agency details'} onPress={submit} disabled={!ready} busy={busy} testID="submit-agency" />
      {mode === 'edit' && initial?.verification_status === 'verified' ? (
        <P small muted>Changes to legal details (name, type, owners, PAN, GST, RERA) are re-checked by ops; you keep working meanwhile.</P>
      ) : null}
    </>
  );
}
