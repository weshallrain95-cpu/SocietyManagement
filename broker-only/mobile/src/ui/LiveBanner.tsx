import * as Haptics from 'expo-haptics';
import { router } from 'expo-router';
import React, { useEffect } from 'react';
import { Platform, Pressable, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useSession } from '@/auth/session';
import { useQueryClient } from '@tanstack/react-query';

import { font, radius, space, usePalette } from './theme';

const TITLES: Record<string, string> = {
  'enquiry.new': 'New enquiry near you',
  'proposal.accepted': 'A customer accepted your proposal',
  'enquiry.closed': 'An enquiry was closed',
  'visit_plan.updated': 'A visit plan changed',
  'visit_stop.assigned': 'You have new visits',
  'visit_plan.team_assigned': 'A manager assigned visits',
  'status.changed': 'A flat you list changed status',
};

/** The "beep": a banner + haptic when something arrives over the live connection. */
export function LiveBanner() {
  const { lastEvent, dismissEvent } = useSession();
  const qc = useQueryClient();
  const c = usePalette();
  const insets = useSafeAreaInsets();

  useEffect(() => {
    if (!lastEvent) return;
    if (Platform.OS !== 'web') Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success).catch(() => {});
    qc.invalidateQueries();
    const t = setTimeout(dismissEvent, 12_000);
    return () => clearTimeout(t);
  }, [lastEvent]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!lastEvent) return null;
  const title = TITLES[lastEvent.event] ?? 'Update';
  const summary = typeof lastEvent.data.summary === 'string' ? lastEvent.data.summary : '';
  const matches = typeof lastEvent.data.match_count === 'number' ? ` · ${lastEvent.data.match_count} of your flats match` : '';
  return (
    <View pointerEvents="box-none" style={{ position: 'absolute', top: insets.top + 8, left: 12, right: 12, zIndex: 100 }}>
      <Pressable
        accessibilityRole="alert"
        onPress={() => {
          dismissEvent();
          if (lastEvent.event.startsWith('enquiry')) router.push('/leads');
          else if (lastEvent.event.startsWith('visit')) router.push('/today');
        }}
        style={{ backgroundColor: c.brand, borderRadius: radius.md, padding: space.md, gap: 2, shadowColor: '#000', shadowOpacity: 0.2, shadowRadius: 8, elevation: 6 }}
      >
        <Text style={{ color: c.brandText, fontWeight: '700', fontSize: font.body }}>🔔 {title}</Text>
        {summary ? <Text style={{ color: c.brandText, fontSize: font.small }} numberOfLines={2}>{summary}{matches}</Text> : null}
        <Text style={{ color: c.brandText, fontSize: font.small, opacity: 0.8 }}>Tap to open</Text>
      </Pressable>
    </View>
  );
}
