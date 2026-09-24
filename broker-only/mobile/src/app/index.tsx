import { Redirect } from 'expo-router';

import { useSession } from '@/auth/session';
import { Loading, Screen } from '@/ui/components';

export default function Index() {
  const { ready, tokens, isStaff, isOwner } = useSession();
  if (!ready) return <Screen><Loading /></Screen>;
  if (!tokens) return <Redirect href="/login" />;
  return <Redirect href={isOwner ? '/my-flats' : isStaff ? '/day' : '/today'} />;
}
