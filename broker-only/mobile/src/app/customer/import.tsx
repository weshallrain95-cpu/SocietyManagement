// CRM-11: bring the broker's whole existing customer list in at once (their second asset, after inventory).
import { useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { Button, Notice, P, Screen } from '@/ui/components';
import { ImportPanel } from '@/ui/ImportPanel';
import { NeedsPermission } from '@/ui/NeedsPermission';

function ImportCustomersScreen() {
  const { api } = useSession();
  const qc = useQueryClient();
  return (
    <Screen>
      <P muted>Your customer list stays yours: no other broker ever sees it. Numbers already in your book are not duplicated.</P>
      <ImportPanel what="my customers" columns="Name, Mobile, Remarks" run={api.importCustomers} onDone={() => qc.invalidateQueries({ queryKey: ['customers'] })} />
      <Notice>Imported customers get your updates in the app once they log in with their number. Until then, each update gives you a one-tap WhatsApp message for them.</Notice>
      <Button kind="secondary" title="📣 Send them an update" onPress={() => router.push('/broadcast')} />
    </Screen>
  );
}

export default function ImportCustomers() {
  return (
    <NeedsPermission perm="uploads">
      <ImportCustomersScreen />
    </NeedsPermission>
  );
}
