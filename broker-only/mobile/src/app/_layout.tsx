import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { View } from 'react-native';

import { SessionProvider } from '@/auth/session';
import { LiveBanner } from '@/ui/LiveBanner';
import { usePalette } from '@/ui/theme';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 15_000 } },
});

function Shell() {
  const c = usePalette();
  return (
    <View style={{ flex: 1, backgroundColor: c.bg }}>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: c.surface },
          headerTintColor: c.brand,
          headerTitleStyle: { color: c.text, fontWeight: '700' },
          contentStyle: { backgroundColor: c.bg },
          headerBackTitle: 'Back',
        }}
      >
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="(broker)" options={{ headerShown: false }} />
        <Stack.Screen name="(staff)" options={{ headerShown: false }} />
        <Stack.Screen name="(owner)" options={{ headerShown: false }} />
        <Stack.Screen name="(customer)" options={{ headerShown: false }} />
        <Stack.Screen name="settings" options={{ title: 'Settings' }} />
        <Stack.Screen name="listing/new" options={{ title: 'Add flat' }} />
        <Stack.Screen name="listing/[id]" options={{ title: 'Flat' }} />
        <Stack.Screen name="customer/new" options={{ title: 'New customer' }} />
        <Stack.Screen name="customer/[id]" options={{ title: 'Customer' }} />
        <Stack.Screen name="customer/requirement" options={{ title: 'Requirement' }} />
        <Stack.Screen name="match/[reqId]" options={{ title: 'Matching flats' }} />
        <Stack.Screen name="visit/[id]" options={{ title: 'Visit plan' }} />
        <Stack.Screen name="visit/new" options={{ title: 'Plan a visit' }} />
        <Stack.Screen name="broadcast" options={{ title: 'Update my customers' }} />
        <Stack.Screen name="customer/import" options={{ title: 'Import customers' }} />
        <Stack.Screen name="trade/index" options={{ title: 'Co-broking' }} />
        <Stack.Screen name="trade/blast" options={{ title: 'Send to fellow brokers' }} />
        <Stack.Screen name="trade/contacts" options={{ title: 'My fellow brokers' }} />
        <Stack.Screen name="trade/[id]" options={{ title: 'Sent to fellow brokers' }} />
        <Stack.Screen name="society/[id]" options={{ title: 'Building' }} />
        <Stack.Screen name="owner/new" options={{ title: 'Add my flat' }} />
        <Stack.Screen name="owner/[id]" options={{ title: 'My flat' }} />
        <Stack.Screen name="owner/brokers" options={{ title: 'Brokers near my flat' }} />
        <Stack.Screen name="lead/[id]" options={{ title: 'Enquiry' }} />
        <Stack.Screen name="enquiry/new" options={{ title: 'My requirement' }} />
        <Stack.Screen name="enquiry/[id]" options={{ title: 'My request' }} />
      </Stack>
      <LiveBanner />
    </View>
  );
}

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider>
        <Shell />
      </SessionProvider>
    </QueryClientProvider>
  );
}
