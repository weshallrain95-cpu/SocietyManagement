import Ionicons from '@expo/vector-icons/Ionicons';
import { useQuery } from '@tanstack/react-query';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

export default function OwnerTabs() {
  const { tokens, isOwner, api } = useSession();
  const c = usePalette();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me, enabled: isOwner, refetchOnMount: 'always' });
  if (!tokens) return <Redirect href="/login" />;
  if (!isOwner) return <Redirect href="/" />;
  // First visit: a short welcome before anything else.
  if (me.data && !me.isFetching && !me.data.profile?.owner?.welcomed_at) return <Redirect href="/welcome?as=owner" />;
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: c.brand, tabBarInactiveTintColor: c.textMuted, headerStyle: { backgroundColor: c.surface }, headerTitleStyle: { color: c.text, fontWeight: '700' }, tabBarStyle: { backgroundColor: c.surface, borderTopColor: c.border }, sceneStyle: { backgroundColor: c.bg } }}>
      <Tabs.Screen name="my-flats" options={{ title: 'My flats', tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="owner-account" options={{ title: 'Account', tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" color={color as string} size={size} /> }} />
    </Tabs>
  );
}
