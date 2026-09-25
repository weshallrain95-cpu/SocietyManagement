// Enquiry composer (MKT-03): what the customer needs, where, and house-rule needs (conduct only). One request
// reaches every verified broker serving the area; the customer's number stays hidden until they accept an offer.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import type { TxnType } from '@/api';
import { useSession } from '@/auth/session';
import { inr } from '@/lib/format';
import { Button, Chip, ChipRow, ErrorBox, Field, H2, Loading, Notice, P, Screen } from '@/ui/components';

const BHKS = [
  { v: 0.5, label: '1 RK' }, { v: 1, label: '1 BHK' }, { v: 2, label: '2 BHK' }, { v: 3, label: '3 BHK' }, { v: 4, label: '4+ BHK' },
];
const RADII = [1000, 2000, 3000, 5000];

export default function NewEnquiry() {
  const { api } = useSession();
  const qc = useQueryClient();
  const params = useLocalSearchParams<{ locality?: string; txn?: string }>();
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities });
  const [txn, setTxn] = useState<TxnType>(params.txn === 'SALE_RESALE' ? 'SALE_RESALE' : 'RENT');
  const [bhks, setBhks] = useState<number[]>([2]);
  const [budget, setBudget] = useState('');
  const [picked, setLocalityId] = useState<string | undefined>(params.locality);
  const [radius, setRadius] = useState(3000);
  const [urgent, setUrgent] = useState(false);
  const [pets, setPets] = useState<'' | 'cat' | 'dog'>('');
  const [nonveg, setNonveg] = useState(false);
  const [bachelors, setBachelors] = useState(false);
  const [notes, setNotes] = useState('');
  const localityId = picked ?? localities.data?.[0]?.id;

  const rent = txn === 'RENT';
  const amount = Number(budget.replace(/[^\d]/g, '')) || 0;
  const locality = localities.data?.find((l) => l.id === localityId);
  const ready = bhks.length > 0 && amount >= (rent ? 1000 : 100000) && !!locality;
  const post = useMutation({
    mutationFn: () =>
      api.createEnquiry({
        txn_type: txn,
        bhk_min: Math.min(...bhks),
        bhk_max: Math.max(...bhks),
        budget_max: amount,
        center: locality!.centroid,
        radius_m: radius,
        area_label: locality!.name,
        urgency: urgent ? 'urgent' : 'normal',
        house_rule_needs: { ...(pets ? { pets } : {}), ...(nonveg ? { nonveg_cooking: true } : {}), ...(bachelors ? { bachelors: true } : {}) },
        notes: notes.trim() || undefined,
      }),
    onSuccess: (e) => {
      qc.invalidateQueries({ queryKey: ['my-enquiries'] });
      router.replace(`/enquiry/${e.id}`);
    },
  });

  return (
    <Screen>
      <H2>1 · Rent or buy</H2>
      <ChipRow>
        <Chip label="Rent" selected={rent} onPress={() => setTxn('RENT')} />
        <Chip label="Buy" selected={!rent} onPress={() => setTxn('SALE_RESALE')} />
      </ChipRow>

      <H2>2 · Size</H2>
      <ChipRow>
        {BHKS.map((b) => (
          <Chip key={b.v} label={b.label} selected={bhks.includes(b.v)} onPress={() => setBhks(bhks.includes(b.v) ? bhks.filter((x) => x !== b.v) : [...bhks, b.v])} />
        ))}
      </ChipRow>

      <H2>3 · Budget</H2>
      <Field
        label={rent ? 'Up to (₹ per month)' : 'Up to (₹)'}
        keyboardType="number-pad"
        value={budget}
        onChangeText={setBudget}
        placeholder={rent ? '25000' : '9500000'}
        hint={amount ? `Up to ${inr(amount, rent)}` : undefined}
        testID="budget"
      />

      <H2>4 · Where</H2>
      {localities.isLoading ? <Loading /> : null}
      <ChipRow>
        {localities.data?.map((l) => <Chip key={l.id} label={l.name} selected={l.id === localityId} onPress={() => setLocalityId(l.id)} />)}
      </ChipRow>
      <ChipRow>
        {RADII.map((r) => <Chip key={r} label={`within ${r / 1000} km`} selected={radius === r} onPress={() => setRadius(r)} />)}
      </ChipRow>

      <H2>5 · When</H2>
      <ChipRow>
        <Chip label="In the next few weeks" selected={!urgent} onPress={() => setUrgent(false)} />
        <Chip label="Urgent" selected={urgent} onPress={() => setUrgent(true)} />
      </ChipRow>

      {rent ? (
        <>
          <H2>6 · Your household</H2>
          <P small muted>Only what affects the society’s rules. Brokers use this to skip flats that won’t work for you.</P>
          <ChipRow>
            <Chip label="No pets" selected={pets === ''} onPress={() => setPets('')} />
            <Chip label="Cat" selected={pets === 'cat'} onPress={() => setPets('cat')} />
            <Chip label="Dog" selected={pets === 'dog'} onPress={() => setPets('dog')} />
          </ChipRow>
          <ChipRow>
            <Chip label="We cook non-veg" selected={nonveg} onPress={() => setNonveg(!nonveg)} />
            <Chip label="Bachelors / sharing" selected={bachelors} onPress={() => setBachelors(!bachelors)} />
          </ChipRow>
        </>
      ) : null}

      <Field label="Anything else? (optional)" value={notes} onChangeText={setNotes} placeholder="Near the station, high floor, gas pipeline" multiline maxLength={500} />

      {post.error ? <ErrorBox error={post.error} /> : null}
      <Button title="Send to brokers" onPress={() => post.mutate()} disabled={!ready} busy={post.isPending} testID="send-enquiry" />
      <Notice>Your phone number is hidden. Brokers see only what you wrote here, and get your number only if you accept their offer.</Notice>
    </Screen>
  );
}
