// First visit as a customer or an owner (founder decision 2026-09-25): a short, warm welcome. We learn their name
// and a few answers that shape what they see next, and say plainly what we promise them.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { Text, View } from 'react-native';

import type { MeUpdate } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Chip, ChipRow, ErrorBox, Field, P, Screen } from '@/ui/components';
import { usePalette } from '@/ui/theme';

type Opt<T extends string> = { value: T; label: string }[];
const LANGS: Opt<'en' | 'hi' | 'mr'> = [{ value: 'en', label: 'English' }, { value: 'hi', label: 'हिंदी' }, { value: 'mr', label: 'मराठी' }];
const CONTACT: Opt<'call' | 'whatsapp'> = [{ value: 'whatsapp', label: 'WhatsApp' }, { value: 'call', label: 'Phone call' }];

function Pick<T extends string>({ label, options, value, onChange }: { label: string; options: Opt<T>; value?: T; onChange: (v: T) => void }) {
  return (
    <View style={{ gap: 6 }}>
      <P style={{ fontWeight: '700' }}>{label}</P>
      <ChipRow>{options.map((o) => <Chip key={o.value} label={o.label} selected={value === o.value} onPress={() => onChange(o.value)} />)}</ChipRow>
    </View>
  );
}

export default function Welcome() {
  const { as } = useLocalSearchParams<{ as: 'customer' | 'owner' }>();
  const owner = as === 'owner';
  const { api } = useSession();
  const qc = useQueryClient();
  const c = usePalette();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me });
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities, enabled: !owner });
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [lang, setLang] = useState<'en' | 'hi' | 'mr'>('en');
  const [contact, setContact] = useState<'call' | 'whatsapp'>('whatsapp');
  const [intent, setIntent] = useState<'rent' | 'buy'>();
  const [moveIn, setMoveIn] = useState<'now' | '1-3m' | 'exploring'>();
  const [areas, setAreas] = useState<string[]>([]);
  const [flats, setFlats] = useState<'1' | '2-3' | '4+'>();
  const [plan, setPlan] = useState<'rent' | 'sell' | 'both' | 'records'>();
  const fullName = name || me.data?.display_name || '';
  const first = fullName.trim().split(/\s+/)[0];

  const save = useMutation({
    mutationFn: (body: MeUpdate) => api.updateMe(body),
    onSuccess: (m) => {
      qc.setQueryData(['me'], m);
      if (owner) router.replace(flats ? '/owner/new' : '/my-flats');
      else router.replace('/find');
    },
  });
  const submit = () =>
    save.mutate({
      display_name: fullName.trim(),
      ...(email.trim() ? { email: email.trim() } : {}),
      preferred_lang: lang,
      profile: owner
        ? { owner: { ...(flats ? { flats } : {}), ...(plan ? { plan } : {}), contact, welcomed: true } }
        : { customer: { ...(intent ? { intent } : {}), ...(moveIn ? { move_in: moveIn } : {}), areas, contact, welcomed: true } },
    });

  return (
    <Screen>
      <View style={{ marginTop: 24, gap: 6 }}>
        <Text style={{ fontSize: 28, fontWeight: '800', color: c.brand }}>{first ? `Welcome, ${first}` : 'Welcome to Only Broker'}</Text>
        <P muted>{owner ? 'Your flat, your rules. A few quick details and you’re set.' : 'Let’s find you the right home. A few quick details and you’re set.'}</P>
      </View>

      <Field label="Your full name" value={name || me.data?.display_name || ''} onChangeText={setName} placeholder={owner ? 'Anil Deshpande' : 'Riya Kapoor'} testID="welcome-name" />

      {owner ? (
        <>
          <Pick label="How many flats do you own?" value={flats} onChange={setFlats} options={[{ value: '1', label: 'One' }, { value: '2-3', label: '2–3' }, { value: '4+', label: '4 or more' }]} />
          <Pick label="What would you like to do?" value={plan} onChange={setPlan} options={[{ value: 'rent', label: 'Rent it out' }, { value: 'sell', label: 'Sell' }, { value: 'both', label: 'Both' }, { value: 'records', label: 'Just keep my records' }]} />
        </>
      ) : (
        <>
          <Pick label="Looking to" value={intent} onChange={setIntent} options={[{ value: 'rent', label: 'Rent' }, { value: 'buy', label: 'Buy' }]} />
          <Pick label="When do you plan to move?" value={moveIn} onChange={setMoveIn} options={[{ value: 'now', label: 'This month' }, { value: '1-3m', label: 'In 1–3 months' }, { value: 'exploring', label: 'Just exploring' }]} />
          <View style={{ gap: 6 }}>
            <P style={{ fontWeight: '700' }}>Areas you like (optional)</P>
            <ChipRow>
              {localities.data?.map((l) => <Chip key={l.id} label={l.name} selected={areas.includes(l.id)} onPress={() => setAreas(areas.includes(l.id) ? areas.filter((x) => x !== l.id) : [...areas, l.id])} />)}
            </ChipRow>
          </View>
        </>
      )}

      <Pick label="How should brokers reach you?" value={contact} onChange={setContact} options={CONTACT} />
      <Pick label="Language for messages" value={lang} onChange={setLang} options={LANGS} />
      <Field label="Email (optional)" keyboardType="email-address" autoCapitalize="none" value={email} onChangeText={setEmail} />

      <View style={{ backgroundColor: c.surface, borderRadius: 14, padding: 14, gap: 6, borderWidth: 1, borderColor: c.border }}>
        <P style={{ fontWeight: '700' }}>Our promise to you</P>
        {(owner
          ? ['A broker handles your flat only if you tick “Allow this broker”.', 'Remove any broker any time; they are told at once.', 'Photos and videos are shared only after you approve them.']
          : ['Your number stays private until you accept a broker’s offer.', 'Brokers see what you need, never who you are.', 'Stop any broker’s updates with one tap.']
        ).map((t) => <P key={t} small muted>✓ {t}</P>)}
      </View>

      {save.error ? <ErrorBox error={save.error} /> : null}
      <Button title={owner ? (flats ? 'Add my first flat' : 'Continue') : 'Start finding homes'} onPress={submit} disabled={fullName.trim().length < 2} busy={save.isPending} testID="welcome-go" />
    </Screen>
  );
}
