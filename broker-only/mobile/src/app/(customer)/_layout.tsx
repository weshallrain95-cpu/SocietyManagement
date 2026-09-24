import Ionicons from '@expo/vector-icons/Ionicons';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

export default function CustomerTabs() {
  const { tokens, role } = useSession();
  const c = usePalette();
  if (!tokens) return <Redirect href="/login" />;
  if (role !== 'customer') return <Redirect href="/" />;
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: c.brand, tabBarInactiveTintColor: c.textMuted, headerStyle: { backgroundColor: c.surface }, headerTitleStyle: { color: c.text, fontWeight: '700' }, tabBarStyle: { backgroundColor: c.surface, borderTopColor: c.border }, sceneStyle: { backgroundColor: c.bg } }}>
      <Tabs.Screen name="updates" options={{ title: 'Updates', tabBarIcon: ({ color, size }) => <Ionicons name="notifications-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="customer-account" options={{ title: 'Account', tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" color={color as string} size={size} /> }} />
    </Tabs>
  );
}
