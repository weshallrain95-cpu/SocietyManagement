import { router } from 'expo-router';
import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, Text, View } from 'react-native';

import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import type { TxnType } from '@/api';
import { Button, Card, Chip, ChipRow, ErrorBox, Field, Notice, P, Screen } from '@/ui/components';
import { font, space, usePalette } from '@/ui/theme';

export default function Login() {
  const { api, signIn, settings, updateSettings } = useSession();
  const c = usePalette();
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState<'phone' | 'otp' | 'register'>('phone');
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
      if (t.org || t.role === 'owner' || (t.role === 'customer' && !t.new_user)) router.replace('/');
      else setStep('register'); // signed in, but not yet part of a broker agency
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }

  async function becomeOwner() {
    setBusy(true);
    setError(null);
    try {
      await signIn(await api.switchRole('owner'));
      router.replace('/');
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
    setPhone('9820000001');
    setStep('phone');
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <Screen>
        <View style={{ marginTop: 48, marginBottom: space.lg, gap: space.xs }}>
          <Text style={{ fontSize: 34, fontWeight: '800', color: c.brand }}>Only Broker</Text>
          <P muted>Your flats, customers and site visits — in one place.</P>
        </View>

        {step === 'phone' ? (
          <>
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
            <Card>
              <P style={{ fontWeight: '700' }}>Own a flat?</P>
              <P small muted>Add your flat, upload photos and choose which brokers may handle it.</P>
              <Button kind="secondary" title="I’m a property owner" onPress={becomeOwner} busy={busy} testID="i-am-owner" />
            </Card>
            <Card>
              <P style={{ fontWeight: '700' }}>Looking for a flat?</P>
              <P small muted>See updates from the brokers you deal with.</P>
              <Button kind="secondary" title="I’m looking for a flat" onPress={() => router.replace('/updates')} testID="i-am-customer" />
            </Card>
            <P>Broker? Register your agency to start. (Field staff: ask your principal to add your number instead.)</P>
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
