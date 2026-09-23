// Requirement form. Must-haves come from the approved attribute dictionary (matchable, essential/recommended tiers).
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';

import type { TxnType } from '@/api';
import { useSession } from '@/auth/session';
import { Button, Chip, ChipRow, Choice, ErrorBox, Field, H2, Notice, P, Screen } from '@/ui/components';

const BHK = ['0.5', '1', '1.5', '2', '2.5', '3', '4'];

export default function RequirementForm() {
  const { customerId } = useLocalSearchParams<{ customerId: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const locs = useQuery({ queryKey: ['localities'], queryFn: api.localities });
  const dict = useQuery({ queryKey: ['dict', 'must'], queryFn: () => api.dictionary({ tier: 'essential,recommended', matchable: true }) });
  const [txn, setTxn] = useState<TxnType>('RENT');
  const [bhks, setBhks] = useState<string[]>(['2']);
  const [budget, setBudget] = useState('');
  const [localityIds, setLocalityIds] = useState<string[]>([]);
  const [musts, setMusts] = useState<string[]>([]);
  const [needs, setNeeds] = useState<Record<string, unknown>>({});
  const [occupants, setOccupants] = useState('');

  const toggle = (arr: string[], v: string) => (arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]);
  const nums = bhks.map(Number).sort((a, b) => a - b);
  const budgetNum = Number(budget.replace(/[^\d]/g, ''));
  // Must-have chips: booleans only in the quick form (e.g. lift, gas stove, gym). House rules are handled below.
  const mustOptions = (dict.data ?? []).filter((d) => d.type === 'bool' && !d.category.toLowerCase().includes('house rule')).slice(0, 14);

  const save = useMutation({
    mutationFn: () =>
      api.addRequirement(customerId, {
        txn_type: txn,
        bhk_min: nums[0],
        bhk_max: nums[nums.length - 1],
        budget_max: budgetNum,
        locality_ids: localityIds,
        must_haves: Object.fromEntries(musts.map((k) => [k, true])),
        house_rule_needs: needs,
        occupants: occupants ? Number(occupants) : null,
      }),
    onSuccess: (r) => {
      qc.invalidateQueries({ queryKey: ['customer', customerId] });
      router.replace({ pathname: '/match/[reqId]', params: { reqId: r.id, customerId } });
    },
  });

  return (
    <Screen>
      <Choice label="Looking to" value={txn} onChange={setTxn} options={[{ value: 'RENT', label: 'Rent' }, { value: 'SALE_RESALE', label: 'Buy (resale)' }, { value: 'SALE_NEW', label: 'Buy (new)' }]} />
      <P small style={{ fontWeight: '600' }}>Configuration (pick one or more)</P>
      <ChipRow>{BHK.map((b) => <Chip key={b} label={b === '0.5' ? '1 RK' : `${b} BHK`} selected={bhks.includes(b)} onPress={() => setBhks((x) => (x.length === 1 && x[0] === b ? x : toggle(x, b)))} />)}</ChipRow>
      <Field label={txn === 'RENT' ? 'Max rent per month (₹)' : 'Max budget (₹)'} keyboardType="number-pad" value={budget} onChangeText={setBudget} testID="budget" />

      <H2>Where</H2>
      <ChipRow>{locs.data?.map((l) => <Chip key={l.id} label={l.name} selected={localityIds.includes(l.id)} onPress={() => setLocalityIds((x) => toggle(x, l.id))} />)}</ChipRow>

      <H2>Must have</H2>
      <ChipRow>{mustOptions.map((d) => <Chip key={d.key} label={d.label} selected={musts.includes(d.key)} onPress={() => setMusts((x) => toggle(x, d.key))} />)}</ChipRow>

      <H2>How they will live there</H2>
      <P small muted>Conduct-based needs only. Flats whose house rules clash are removed before you visit.</P>
      <ChipRow>
        {[['pets', 'dog', 'Has a dog'], ['pets', 'cat', 'Has a cat'], ['nonveg_cooking', true, 'Cooks non-veg'], ['bachelors', true, 'Bachelors'], ['smoking', true, 'Smokes'], ['company_lease', true, 'Company lease']].map(([k, v, label]) => {
          const on = needs[k as string] === v;
          return <Chip key={label as string} label={label as string} selected={on} onPress={() => setNeeds((n) => { const m = { ...n }; if (on) delete m[k as string]; else m[k as string] = v; return m; })} />;
        })}
      </ChipRow>
      <Field label="Number of occupants (optional)" keyboardType="number-pad" value={occupants} onChangeText={setOccupants} />

      <Notice>Unknown details never hide a flat — they show as “≈ not confirmed” so you can check with the owner.</Notice>
      {save.error ? <ErrorBox error={save.error} /> : null}
      <Button title="Save and find flats" onPress={() => save.mutate()} disabled={!budgetNum || !bhks.length} busy={save.isPending} testID="save-req" />
    </Screen>
  );
}
