import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { Button, Notice, P, Screen } from '@/ui/components';

export default function OwnerAccount() {
  const { signOut, settings } = useSession();
  return (
    <Screen>
      <P muted>Owner account{settings.demo ? ' (demo)' : ''}</P>
      <Notice>
        Only brokers you allow can handle your flat. Untick a broker on your flat’s page at any time — your decision is final.
        Your proof of ownership is private: brokers and customers never see it.
      </Notice>
      <Button kind="danger" title="Sign out" onPress={async () => { await signOut(); router.replace('/login'); }} />
    </Screen>
  );
}
