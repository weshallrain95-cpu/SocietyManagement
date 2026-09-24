import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { ago, CONSENT_LABEL, phone } from '@/lib/format';
import { Button, Card, Chip, ErrorBox, Field, H1, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';

const KIND_LABEL: Record<string, string> = {
  call_in: '📞 Incoming call', call_out: '📞 Called', office_meeting: '🏢 Office meeting', whatsapp: '💬 WhatsApp', sms: '✉️ SMS',
  link_opened: '🔗 Opened link', shortlist_response: '⭐ Shortlist', visit: '🚶 Visit', note: '📝 Note', system: 'ℹ️ Update',
};

export default function CustomerDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const c = useQuery({ queryKey: ['customer', id], queryFn: () => api.customer(id) });
  const tl = useQuery({ queryKey: ['timeline', id], queryFn: () => api.timeline(id) });
  const [otp, setOtp] = useState('');
  const [devCode, setDevCode] = useState<string | undefined>();
  const [note, setNote] = useState('');
  const refresh = () => {
    qc.invalidateQueries({ queryKey: ['customer', id] });
    qc.invalidateQueries({ queryKey: ['timeline', id] });
  };
  const consent = useMutation({
    mutationFn: (m: 'otp' | 'link' | 'attested') => api.requestConsent(id, m, m === 'attested' ? 'Agreed verbally' : undefined),
    onSuccess: (r) => {
      setDevCode(r.dev_code);
      refresh();
    },
  });
  const verify = useMutation({ mutationFn: () => api.verifyConsent(id, otp), onSuccess: refresh });
  const log = useMutation({ mutationFn: (kind: string) => api.logInteraction(id, { kind, summary: note }), onSuccess: () => { setNote(''); refresh(); } });

  if (c.isLoading) return <Screen><Loading /></Screen>;
  if (!c.data) return <Screen><ErrorBox error={c.error} onRetry={c.refetch} /></Screen>;
  const cu = c.data;
  const needsConsent = !cu.can_message;

  return (
    <Screen onRefresh={refresh} refreshing={c.isFetching}>
      <H1>{cu.name || cu.phone}</H1>
      <P muted>{phone(cu.phone)} · {cu.stage.replace(/_/g, ' ')}{cu.on_platform ? ' · on the app' : ''}</P>

      <H2>Consent</H2>
      <Card>
        <P style={{ fontWeight: '600' }}>{CONSENT_LABEL[cu.consent_state]}</P>
        {needsConsent ? (
          <>
            <P small muted>Before we send shortlists or visit plans on WhatsApp/SMS, the customer must agree. Pick what suits the moment:</P>
            <Row style={{ flexWrap: 'wrap' }}>
              <Button small title="Send OTP" onPress={() => consent.mutate('otp')} busy={consent.isPending} />
              <Button small kind="secondary" title="Send link" onPress={() => consent.mutate('link')} />
              <Button small kind="secondary" title="Agreed verbally" onPress={() => consent.mutate('attested')} />
            </Row>
            {consent.data?.sent === 'otp' ? (
              <>
                <Field label="OTP the customer reads out" keyboardType="number-pad" maxLength={6} value={otp} onChangeText={setOtp} />
                {devCode ? <Notice>Development mode: OTP is {devCode}</Notice> : null}
                <Button small title="Confirm consent" onPress={() => verify.mutate()} disabled={otp.length !== 6} busy={verify.isPending} />
              </>
            ) : null}
            {consent.data?.sent === 'link' ? <Notice tone="ok">Consent link sent to the customer’s phone.</Notice> : null}
          </>
        ) : null}
        {consent.error || verify.error ? <ErrorBox error={consent.error ?? verify.error} /> : null}
      </Card>

      <Button kind="secondary" title="Plan a visit — pick flats yourself" onPress={() => router.push({ pathname: '/visit/new', params: { customerId: id, customerName: cu.name } })} testID="plan-own" />

      <H2 right={<Button small kind="ghost" title="+ Requirement" onPress={() => router.push({ pathname: '/customer/requirement', params: { customerId: id } })} />}>Requirements</H2>
      {cu.requirements?.length ? null : <Notice tone="warn">No requirement yet. Add one to see matching flats from your inventory.</Notice>}
      {cu.requirements?.map((r) => (
        <Card key={r.id}>
          <P>{r.summary}</P>
          <Row>
            <Button small title="Find matching flats" onPress={() => router.push({ pathname: '/match/[reqId]', params: { reqId: r.id, customerId: id } })} testID="find-matches" />
            {r.version > 1 ? <Chip label={`v${r.version}`} /> : null}
          </Row>
        </Card>
      ))}

      <H2>Log a call or meeting</H2>
      <Field label="What happened" value={note} onChangeText={setNote} placeholder="e.g. Wants to see flats on Saturday" multiline />
      <Row style={{ flexWrap: 'wrap' }}>
        {[['call_in', 'Incoming call'], ['call_out', 'I called'], ['office_meeting', 'Office visit'], ['whatsapp', 'WhatsApp']].map(([k, label]) => (
          <Button key={k} small kind="secondary" title={label} disabled={!note.trim()} onPress={() => log.mutate(k)} />
        ))}
      </Row>

      <H2>History</H2>
      {tl.data?.length === 0 ? <P muted small>Nothing yet.</P> : null}
      {tl.data?.map((t) => (
        <Row key={t.id} style={{ alignItems: 'flex-start' }}>
          <P small style={{ width: 112 }}>{KIND_LABEL[t.kind] ?? t.kind}</P>
          <P small style={{ flex: 1 }}>{t.summary}</P>
          <P small muted>{ago(t.at)}</P>
        </Row>
      ))}
    </Screen>
  );
}
