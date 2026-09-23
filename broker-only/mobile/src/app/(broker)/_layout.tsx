import Ionicons from '@expo/vector-icons/Ionicons';
import { Redirect, Tabs } from 'expo-router';
import React from 'react';
import type { ColorValue } from 'react-native';

import { useSession } from '@/auth/session';
import { usePalette } from '@/ui/theme';

type IconName = React.ComponentProps<typeof Ionicons>['name'];
const icon = (name: IconName) =>
  function TabIcon({ color, size }: { color: ColorValue; size: number }) {
    return <Ionicons name={name} color={color as string} size={size} />;
  };

export default function BrokerTabs() {
  const { tokens, isStaff } = useSession();
  const c = usePalette();
  if (!tokens) return <Redirect href="/login" />;
  if (isStaff) return <Redirect href="/day" />;
  return (
    <Tabs
      screenOptions={{
        headerStyle: { backgroundColor: c.surface },
        headerTitleStyle: { color: c.text, fontWeight: '700' },
        tabBarActiveTintColor: c.brand,
        tabBarInactiveTintColor: c.textMuted,
        tabBarStyle: { backgroundColor: c.surface, borderTopColor: c.border },
        sceneStyle: { backgroundColor: c.bg },
      }}
    >
      <Tabs.Screen name="today" options={{ title: 'Today', tabBarIcon: icon('home-outline') }} />
      <Tabs.Screen name="leads" options={{ title: 'Leads', tabBarIcon: icon('flash-outline') }} />
      <Tabs.Screen name="customers" options={{ title: 'Customers', tabBarIcon: icon('people-outline') }} />
      <Tabs.Screen name="inventory" options={{ title: 'Flats', tabBarIcon: icon('business-outline') }} />
      <Tabs.Screen name="more" options={{ title: 'More', tabBarIcon: icon('menu-outline') }} />
    </Tabs>
  );
}
