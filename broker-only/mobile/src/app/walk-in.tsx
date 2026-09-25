// Field staff: a walk-in at the site — number, name and what they're looking for. The customer goes into the
// agency's book (the manager sees it at once); staff see only customers they captured or are visiting.
import { useMutation } from '@tanstack/react-query';
import React, { useState } from 'react';

import type { TxnType } from '@/api';
import { useSession } from '@/auth/session';
import { indianMobile, inr } from '@/lib/format';
import { Button, Chip, ChipRow, ErrorBox, Field, H2, Notice, Screen } from '@/ui/components';

const BHKS = [1, 2, 3, 4];

export default function WalkIn() {
  const { api } = useSession();
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [txn, setTxn] = useState<TxnType>('RENT');
  const [bhk, setBhk] = useState(2);
  const [budget, setBudget] = useState('');
  const [notes, setNotes] = useState('');
  const [saved, setSaved] = useState('');
  const mobile = indianMobile(phone);
  const amount = Number(budget.replace(/[^\d]/g, '')) || 0;
  const rent = txn === 'RENT';
  const save = useMutation({
    mutationFn: async () => {
      const c = await api.captureCustomer({ phone: mobile!, name: name.trim(), source: 'walk_in', notes });
      if (amount) await api.addRequirement(c.id, { txn_type: txn, bhk_min: bhk, bhk_max: bhk, budget_max: amount });
      return c;
    },
    onSuccess: (c) => {
      setSaved(c.name || name || 'The customer');
      setPhone('');
      setName('');
      setBudget('');
      setNotes('');
    },
  });
  return (
    <Screen>
      {saved ? <Notice tone="ok">{saved} is saved in your agency’s customer book. Your manager can see them now.</Notice> : null}
      <Field label="Mobile number" keyboardType="phone-pad" value={phone} onChangeText={(t) => { setPhone(t); setSaved(''); }} testID="walkin-phone"
        error={phone.length >= 10 && !mobile ? 'Enter a valid 10-digit mobile number' : undefined} />
      <Field label="Name" value={name} onChangeText={setName} testID="walkin-name" />
      <H2>Looking for</H2>
      <ChipRow>
        <Chip label="Rent" selected={rent} onPress={() => setTxn('RENT')} />
        <Chip label="Buy" selected={!rent} onPress={() => setTxn('SALE_RESALE')} />
      </ChipRow>
      <ChipRow>
        {BHKS.map((b) => <Chip key={b} label={b === 4 ? '4+ BHK' : `${b} BHK`} selected={bhk === b} onPress={() => setBhk(b)} />)}
      </ChipRow>
      <Field label={rent ? 'Budget up to (₹ per month)' : 'Budget up to (₹)'} keyboardType="number-pad" value={budget} onChangeText={setBudget}
        hint={amount ? `Up to ${inr(amount, rent)}` : 'Optional'} />
      <Field label="Notes (optional)" value={notes} onChangeText={setNotes} multiline placeholder="Wants a high floor, moving next month" />
      {save.error ? <ErrorBox error={save.error} /> : null}
      <Button title="Save walk-in" onPress={() => save.mutate()} disabled={!mobile} busy={save.isPending} testID="save-walkin" />
    </Screen>
  );
}
