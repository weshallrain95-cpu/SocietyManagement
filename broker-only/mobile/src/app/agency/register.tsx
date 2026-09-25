// First time as a broker: register the agency (you become its Admin).
import { useMutation } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { AgencyFormView } from '@/ui/AgencyFormView';
import { Screen } from '@/ui/components';

export default function RegisterAgency() {
  const { api, signIn } = useSession();
  const reg = useMutation({
    mutationFn: api.registerOrg,
    onSuccess: async ({ tokens }) => {
      await signIn(tokens);
      router.replace('/');
    },
  });
  return (
    <Screen>
      <AgencyFormView mode="register" busy={reg.isPending} error={reg.error} onSubmit={(f) => reg.mutate(f)} />
    </Screen>
  );
}
