// Wraps a screen that only the Admin (or a manager the Admin allowed) may use.
import React from 'react';

import type { TeamPermission } from '@/api';
import { PERMISSION_LABEL, useAgency } from '@/auth/useAgency';
import { Loading, Notice, P, Screen } from './components';

export function NeedsPermission({ perm, children }: { perm: TeamPermission; children: React.ReactNode }) {
  const a = useAgency();
  if (a.loading) return <Screen><Loading /></Screen>;
  if (a.can(perm)) return <>{children}</>;
  return (
    <Screen>
      <Notice tone="warn">Only your agency Admin can do this, or a manager the Admin has allowed.</Notice>
      <P muted>Ask your Admin to switch on “{PERMISSION_LABEL[perm]}” for you under More → Team.</P>
    </Screen>
  );
}
