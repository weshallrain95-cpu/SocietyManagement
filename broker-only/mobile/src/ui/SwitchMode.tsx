// One phone number can be a broker, an owner and a customer; the person switches on purpose, never silently.
import { useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';

import { useAgency } from '@/auth/useAgency';
import { useSession } from '@/auth/session';
import { kv } from '@/lib/kv';
import { Button, ErrorBox, H2 } from './components';

type Mode = 'broker' | 'owner' | 'customer';
export const WHO_KEY = 'ob.who';

export function SwitchMode({ current }: { current: Mode }) {
  const { api, signIn } = useSession();
  const qc = useQueryClient();
  const a = useAgency();
  const [error, setError] = useState<unknown>(null);
  const hasAgency = !!a.me?.memberships.length;
  const go = async (to: Mode) => {
    setError(null);
    try {
      await signIn(await api.switchRole(to));
      await kv.setItem(WHO_KEY, to);
      qc.clear();
      router.replace(to === 'customer' ? '/find' : '/');
    } catch (e) {
      setError(e);
    }
  };
  const options: { to: Mode; title: string }[] = [
    ...(current !== 'broker' && hasAgency ? [{ to: 'broker' as Mode, title: `Switch to my agency (${a.me?.memberships[0]?.org_name})` }] : []),
    ...(current !== 'owner' ? [{ to: 'owner' as Mode, title: 'Switch to owner mode (my flats)' }] : []),
    ...(current !== 'customer' ? [{ to: 'customer' as Mode, title: 'Switch to customer mode (find a flat)' }] : []),
  ];
  return (
    <>
      <H2>Switch mode</H2>
      {options.map((o) => (
        <Button key={o.to} kind="secondary" title={o.title} onPress={() => go(o.to)} testID={`switch-${o.to}`} />
      ))}
      {error ? <ErrorBox error={error} /> : null}
    </>
  );
}
