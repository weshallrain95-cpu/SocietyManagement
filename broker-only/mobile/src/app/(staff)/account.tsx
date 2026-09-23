import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { Button, Notice, P, Screen } from '@/ui/components';

export default function Account() {
  const { signOut, queue, settings } = useSession();
  return (
    <Screen>
      <P muted>Field staff account{settings.demo ? ' (demo)' : ''}</P>
      <Notice>Owner phone numbers are hidden from field staff. You see only the flats on your route.</Notice>
      <Button
        kind="danger"
        title="Sign out"
        onPress={async () => {
          if ((await queue.pending()).length) {
            alert('You have visits waiting to sync. Sync before signing out.');
            return;
          }
          await signOut();
          router.replace('/login');
        }}
      />
    </Screen>
  );
}
