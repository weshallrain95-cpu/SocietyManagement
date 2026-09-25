import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { Button, Notice, P, Screen } from '@/ui/components';
import { SwitchMode } from '@/ui/SwitchMode';

export default function CustomerAccount() {
  const { signOut, settings } = useSession();
  return (
    <Screen>
      <P muted>Customer account{settings.demo ? ' (demo)' : ''}</P>
      <Notice>You get updates only from brokers you’ve dealt with. Stop any broker’s updates from the Updates tab.</Notice>
      <SwitchMode current="customer" />
      <Button kind="danger" title="Sign out" onPress={async () => { await signOut(); router.replace('/login'); }} />
    </Screen>
  );
}
