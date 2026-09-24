import Ionicons from '@expo/vector-icons/Ionicons';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

export default function OwnerTabs() {
  const { tokens, isOwner } = useSession();
  const c = usePalette();
  if (!tokens) return <Redirect href="/login" />;
  if (!isOwner) return <Redirect href="/" />;
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: c.brand, tabBarInactiveTintColor: c.textMuted, headerStyle: { backgroundColor: c.surface }, headerTitleStyle: { color: c.text, fontWeight: '700' }, tabBarStyle: { backgroundColor: c.surface, borderTopColor: c.border }, sceneStyle: { backgroundColor: c.bg } }}>
      <Tabs.Screen name="my-flats" options={{ title: 'My flats', tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="owner-account" options={{ title: 'Account', tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" color={color as string} size={size} /> }} />
    </Tabs>
  );
}
