import Ionicons from '@expo/vector-icons/Ionicons';
import { useQuery } from '@tanstack/react-query';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

export default function CustomerTabs() {
  const { tokens, role, api } = useSession();
  const c = usePalette();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me, enabled: role === 'customer', refetchOnMount: 'always' });
  if (!tokens) return <Redirect href="/login" />;
  if (role !== 'customer') return <Redirect href="/" />;
  // First visit: a short welcome before anything else.
  if (me.data && !me.isFetching && !me.data.profile?.customer?.welcomed_at) return <Redirect href="/welcome?as=customer" />;
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: c.brand, tabBarInactiveTintColor: c.textMuted, headerStyle: { backgroundColor: c.surface }, headerTitleStyle: { color: c.text, fontWeight: '700' }, tabBarStyle: { backgroundColor: c.surface, borderTopColor: c.border }, sceneStyle: { backgroundColor: c.bg } }}>
      <Tabs.Screen name="find" options={{ title: 'Find a flat', tabBarIcon: ({ color, size }) => <Ionicons name="search-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="updates" options={{ title: 'Updates', tabBarIcon: ({ color, size }) => <Ionicons name="notifications-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="customer-account" options={{ title: 'Account', tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" color={color as string} size={size} /> }} />
    </Tabs>
  );
}
