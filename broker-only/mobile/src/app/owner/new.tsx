// Owner adds their flat (route 1). The flat must exist in our building universe; proof is kept, never checked.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';
import { Image } from 'react-native';

import type { SocietyCandidate, UploadFile } from '@/api';
import { useSession } from '@/auth/session';
import { canUseCamera, pickFromGallery, takePhoto } from '@/lib/pickMedia';
import { useDebounced } from '@/lib/useDebounced';
import { Button, Card, Chip, ChipRow, Choice, ErrorBox, Field, H2, Notice, P, Row, Screen, Tick } from '@/ui/components';

const BHK = ['0.5', '1', '1.5', '2', '2.5', '3', '4'];

export default function RegisterFlat() {
  const { api } = useSession();
  const qc = useQueryClient();
  const [q, setQ] = useState('');
  const [society, setSociety] = useState<SocietyCandidate | null>(null);
  const [wing, setWing] = useState('');
  const [unitNo, setUnitNo] = useState('');
  const [bhk, setBhk] = useState('2');
  const [proof, setProof] = useState<UploadFile | null>(null);
  const [declared, setDeclared] = useState(false);
  const [pickError, setPickError] = useState<unknown>(null);

  const search = useQuery({ queryKey: ['soc', q], queryFn: () => api.searchSocieties(q), enabled: q.trim().length >= 2 && !society });
  const wingsQ = useQuery({ queryKey: ['wings', society?.society_id], queryFn: () => api.wings(society!.society_id), enabled: !!society });
  const typed = useDebounced(`${wing}|${unitNo.trim()}`, 400);
  const check = useQuery({
    queryKey: ['check-flat', society?.society_id, typed],
    queryFn: () => api.checkFlat(society!.society_id, { wing: typed.split('|')[0] || undefined, unit_no: typed.split('|')[1] }),
    enabled: !!society && !!typed.split('|')[1],
  });
  const save = useMutation({
    mutationFn: () => api.registerFlat({ society_id: society!.society_id, wing: wing || undefined, unit_no: unitNo.trim(), bhk, declared, proof: proof! }),
    onSuccess: (f) => {
      qc.invalidateQueries({ queryKey: ['owner-flats'] });
      router.replace(`/owner/${f.id}`);
    },
  });
  const pick = async (fn: () => Promise<UploadFile[]>) => {
    setPickError(null);
    try {
      const [f] = await fn();
      if (f) setProof(f);
    } catch (e) {
      setPickError(e);
    }
  };
  const wings = wingsQ.data?.wings ?? [];
  const ready = society && unitNo.trim() && proof && declared && !check.data?.blocking;

  return (
    <Screen>
      <H2>1 · Your building</H2>
      {society ? (
        <Card>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{society.name}</P>
            <Button small kind="ghost" title="Change" onPress={() => { setSociety(null); setWing(''); }} />
          </Row>
          <P muted small>{society.locality}</P>
        </Card>
      ) : (
        <>
          <Field label="Society name" placeholder="e.g. Hiranandani Estate" value={q} onChangeText={setQ} autoCorrect={false} hint="Spelling mistakes are fine." testID="owner-society" />
          {search.data?.map((s) => (
            <Card key={s.society_id} onPress={() => setSociety(s)}>
              <P style={{ fontWeight: '600' }}>{s.name}</P>
              <P muted small>{s.locality}</P>
            </Card>
          ))}
          {search.data?.length === 0 ? <Notice tone="warn">We don’t have this society yet. Please ask your broker or write to us — new buildings are added by our team.</Notice> : null}
        </>
      )}

      {society ? (
        <>
          <H2>2 · Your flat</H2>
          {wings.length ? (
            <ChipRow>{wings.map((w) => <Chip key={w.id} label={w.name} selected={wing === w.name} onPress={() => setWing(w.name)} />)}</ChipRow>
          ) : (
            <Field label="Wing / building" value={wing} onChangeText={setWing} autoCapitalize="characters" placeholder="A" />
          )}
          <Field label="Flat number" value={unitNo} onChangeText={setUnitNo} placeholder="1203" testID="owner-unit" />
          {check.data?.issues.map((i) => <Notice key={i.code} tone={i.blocking ? 'bad' : 'warn'}>{i.message}</Notice>)}
          <Choice label="Configuration" value={bhk} onChange={setBhk} options={BHK.map((b) => ({ value: b, label: b === '0.5' ? '1 RK' : `${b} BHK` }))} />

          <H2>3 · Proof that you own it</H2>
          <P small muted>A photo of your index II, society share certificate or electricity bill. It stays private — brokers and customers never see it.</P>
          {proof ? (
            <Card>
              {proof.type.startsWith('image/') ? <Image source={{ uri: proof.uri }} style={{ width: '100%', height: 160, borderRadius: 8 }} resizeMode="cover" /> : null}
              <Row style={{ justifyContent: 'space-between' }}>
                <P small style={{ flexShrink: 1 }}>{proof.name}</P>
                <Button small kind="ghost" title="Change" onPress={() => setProof(null)} />
              </Row>
            </Card>
          ) : (
            <Row style={{ flexWrap: 'wrap' }}>
              <Button small kind="secondary" title="Choose photo" onPress={() => pick(() => pickFromGallery('photo'))} testID="pick-proof" />
              {canUseCamera ? <Button small kind="secondary" title="Take photo" onPress={() => pick(takePhoto)} /> : null}
            </Row>
          )}
          {pickError ? <ErrorBox error={pickError} /> : null}
          <Tick label="I confirm I own this flat (or am authorised by the owner)." checked={declared} onChange={setDeclared} testID="declare" />
          {save.error ? <ErrorBox error={save.error} /> : null}
          <Button title="Add my flat" onPress={() => save.mutate()} disabled={!ready} busy={save.isPending} testID="register-flat" />
          <P small muted>Adding your flat doesn’t give it to any broker. You choose who may handle it.</P>
        </>
      ) : null}
    </Screen>
  );
}
