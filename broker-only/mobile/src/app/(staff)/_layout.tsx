import Ionicons from '@expo/vector-icons/Ionicons';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

export default function StaffTabs() {
  const { tokens, isStaff } = useSession();
  const c = usePalette();
  if (!tokens) return <Redirect href="/login" />;
  if (!isStaff) return <Redirect href="/today" />;
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: c.brand, headerStyle: { backgroundColor: c.surface }, headerTitleStyle: { color: c.text }, sceneStyle: { backgroundColor: c.bg } }}>
      <Tabs.Screen name="day" options={{ title: 'My day', tabBarIcon: ({ color, size }) => <Ionicons name="calendar-outline" color={color as string} size={size} /> }} />
      <Tabs.Screen name="account" options={{ title: 'Account', tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" color={color as string} size={size} /> }} />
    </Tabs>
  );
}
