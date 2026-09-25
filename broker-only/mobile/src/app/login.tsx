import { router } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, Text, View } from 'react-native';

import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { kv } from '@/lib/kv';
import { WHO_KEY } from '@/ui/SwitchMode';
import type { TxnType } from '@/api';
import { Button, Chip, ChipRow, ErrorBox, Field, Notice, P, Row, Screen } from '@/ui/components';
import { font, space, usePalette } from '@/ui/theme';

type Who = 'broker' | 'owner' | 'customer';
const WHO: { key: Who; title: string; short: string; body: string }[] = [
  { key: 'broker', title: 'I’m a broker', short: 'Broker', body: 'Your agency’s flats, customers and site visits — for Admins, managers and field staff.' },
  { key: 'owner', title: 'I own a flat', short: 'Owner', body: 'Add your flat, photos and terms, and choose which brokers may handle it.' },
  { key: 'customer', title: 'I’m looking for a flat', short: 'Customer', body: 'Tell brokers nearby what you need, compare their offers, and get updates.' },
];

export default function Login() {
  const { api, signIn, settings, updateSettings } = useSession();
  const c = usePalette();
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  // Three ways in (founder decision 2026-09-25): broker, owner or customer. Remembered for next time.
  const [who, setWho] = useState<Who | null>(null);
  const [step, setStep] = useState<'who' | 'phone' | 'otp' | 'register'>('who');
  useEffect(() => {
    kv.getItem(WHO_KEY).then((w) => {
      if (w === 'broker' || w === 'owner' || w === 'customer') {
        setWho(w);
        setStep((cur) => (cur === 'who' ? 'phone' : cur));
      }
    });
  }, []);
  const choose = (w: Who) => {
    setWho(w);
    kv.setItem(WHO_KEY, w);
    setStep('phone');
  };
  const [agency, setAgency] = useState('');
  const [rera, setRera] = useState('');
  const [txns, setTxns] = useState<TxnType[]>(['RENT']);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [devCode, setDevCode] = useState<string | undefined>();
  const mobile = indianMobile(phone);

  async function sendOtp() {
    setBusy(true);
    setError(null);
    try {
      const r = await api.requestOtp(mobile!);
      setDevCode(r.dev_code);
      setStep('otp');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  async function verify() {
    setBusy(true);
    setError(null);
    try {
      const t = await api.verifyOtp(mobile!, code.trim());
      await signIn(t);
      if (who === 'broker') {
        if (t.org) router.replace('/');
        else setStep('register'); // signed in, but not part of an agency yet
      } else if (who === 'owner') {
        if (t.role !== 'owner') await signIn(await api.switchRole('owner'));
        router.replace('/');
      } else {
        if (t.role !== 'customer') await signIn(await api.switchRole('customer'));
        router.replace('/find');
      }
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

    async function register() {
    setBusy(true);
    setError(null);
    try {
      const { tokens } = await api.registerOrg({ name: agency.trim(), txn_types: txns, rera_agent_no: rera.trim() || undefined });
      await signIn(tokens);
      router.replace('/');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  async function tryDemo() {
    await updateSettings({ demo: true });
    setPhone(who === 'owner' ? '9820020000' : who === 'customer' ? '9876543210' : '9820000001');
    setStep(who ? 'phone' : 'who');
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <Screen>
        <View style={{ marginTop: 48, marginBottom: space.lg, gap: space.xs }}>
          <Text style={{ fontSize: 34, fontWeight: '800', color: c.brand }}>Only Broker</Text>
          <P muted>Your flats, customers and site visits — in one place.</P>
        </View>

        {step === 'who' ? (
          <>
            <Text style={{ fontSize: font.title, fontWeight: '800', color: c.text }}>Are you…</Text>
            {WHO.map((w) => (
              <Pressable
                key={w.key}
                onPress={() => choose(w.key)}
                accessibilityRole="button"
                style={{ backgroundColor: c.surface, borderRadius: 16, padding: 18, gap: 4, borderWidth: 1, borderColor: c.border }}
                testID={`who-${w.key}`}
              >
                <Text style={{ fontSize: 19, fontWeight: '800', color: c.brand }}>{w.title}</Text>
                <Text style={{ fontSize: 14, color: c.textMuted }}>{w.body}</Text>
              </Pressable>
            ))}
          </>
        ) : step === 'phone' ? (
          <>
            <Row style={{ justifyContent: 'space-between' }}>
              <P muted>Signing in as <Text style={{ fontWeight: '800', color: c.text }}>{WHO.find((w) => w.key === who)?.short}</Text></P>
              <Button small kind="ghost" title="Change" onPress={() => setStep('who')} testID="change-who" />
            </Row>
            <Field
              label="Mobile number"
              placeholder="98200 00001"
              keyboardType="phone-pad"
              autoComplete="tel"
              value={phone}
              onChangeText={setPhone}
              error={phone.length >= 10 && !mobile ? 'Enter a valid 10-digit Indian mobile number' : undefined}
              testID="phone"
            />
            <Button title="Send OTP" onPress={sendOtp} disabled={!mobile} busy={busy} testID="send-otp" />
          </>
        ) : step === 'register' ? (
          <>
            <Notice>This number is not part of an agency yet. Managers and field staff: ask your agency Admin to add +91 {mobile}, then sign in again.</Notice>
            <P style={{ fontWeight: '700' }}>Starting your own agency? Register it — you become its Admin.</P>
            <Field label="Agency / your name" value={agency} onChangeText={setAgency} placeholder="Suresh Realty" />
            <Field label="MahaRERA agent number (optional for rentals)" value={rera} onChangeText={setRera} autoCapitalize="characters" placeholder="A51700000001" />
            <P small style={{ fontWeight: '600' }}>You handle</P>
            <ChipRow>
              {(['RENT', 'SALE_RESALE', 'SALE_NEW'] as TxnType[]).map((t) => (
                <Chip
                  key={t}
                  label={{ RENT: 'Rentals', SALE_RESALE: 'Resale', SALE_NEW: 'New projects' }[t]}
                  selected={txns.includes(t)}
                  onPress={() => setTxns((cur) => (cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]))}
                />
              ))}
            </ChipRow>
            <Button title="Register agency" onPress={register} disabled={agency.trim().length < 3 || !txns.length} busy={busy} />
            <P small muted>Ops verifies new agencies within a working day. You can add flats and customers straight away.</P>
            <Button kind="ghost" title="Not a broker? Go back" onPress={() => setStep('who')} />
          </>
        ) : (
          <>
            <P>OTP sent to +91 {mobile}</P>
            <Field label="6-digit OTP" keyboardType="number-pad" maxLength={6} value={code} onChangeText={setCode} testID="otp" autoFocus />
            {devCode ? <Notice>Development mode: your OTP is {devCode}</Notice> : null}
            <Button title="Verify and continue" onPress={verify} disabled={code.trim().length !== 6} busy={busy} testID="verify" />
            <Button kind="ghost" title="Change number" onPress={() => setStep('phone')} />
          </>
        )}

        {error ? <ErrorBox error={error} /> : null}

        <View style={{ marginTop: space.xl, gap: space.sm }}>
          {settings.demo ? (
            <Notice tone="warn">
              Demo mode: sample Thane West data, nothing leaves this device. Broker: 9820000001 · Field staff: 9820010000 · Owner: 9820020000 · Customer: 9876543210 · OTP 123456
            </Notice>
          ) : (
            <Button kind="secondary" title="Try the demo" onPress={tryDemo} testID="try-demo" />
          )}
          <Button kind="ghost" title="Server settings" onPress={() => router.push('/settings')} />
          <P small muted style={{ textAlign: 'center', fontSize: font.small }}>
            By continuing you agree to the Terms and Privacy Policy.
          </P>
        </View>
      </Screen>
    </KeyboardAvoidingView>
  );
}
