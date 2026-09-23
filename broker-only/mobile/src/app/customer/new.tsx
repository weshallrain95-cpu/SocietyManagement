// OFF-01: capture a walk-in / phone customer in under a minute. They never need the app.
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';

import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { Button, Choice, ErrorBox, Field, Notice, Screen } from '@/ui/components';

export default function NewCustomer() {
  const { api } = useSession();
  const qc = useQueryClient();
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [source, setSource] = useState('walk_in');
  const [notes, setNotes] = useState('');
  const mobile = indianMobile(phone);
  const save = useMutation({
    mutationFn: () => api.captureCustomer({ phone: mobile!, name: name.trim(), source, notes }),
    onSuccess: (c) => {
      qc.invalidateQueries({ queryKey: ['customers'] });
      router.replace(`/customer/${c.id}`);
    },
  });
  return (
    <Screen>
      <Field label="Mobile number" keyboardType="phone-pad" value={phone} onChangeText={setPhone} autoFocus testID="cust-phone"
        error={phone.length >= 10 && !mobile ? 'Enter a valid 10-digit mobile number' : undefined} />
      <Field label="Name" value={name} onChangeText={setName} testID="cust-name" />
      <Choice label="How did they reach you?" value={source} onChange={setSource} options={[
        { value: 'walk_in', label: 'Walk-in' }, { value: 'phone_call', label: 'Phone call' }, { value: 'referral', label: 'Referral' },
        { value: 'whatsapp_group', label: 'WhatsApp group' }, { value: 'board', label: 'Board / hoarding' }, { value: 'other', label: 'Other' },
      ]} />
      <Field label="Notes (optional)" value={notes} onChangeText={setNotes} multiline />
      <Notice>If this number is already in your book, we open the existing customer instead of creating a duplicate.</Notice>
      {save.error ? <ErrorBox error={save.error} /> : null}
      <Button title="Save customer" onPress={() => save.mutate()} disabled={!mobile} busy={save.isPending} testID="save-customer" />
    </Screen>
  );
}
