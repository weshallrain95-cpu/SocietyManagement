// D18: the building as a picture — every wing, floor by floor, from our official sources (TMC property-tax
// register, MahaRERA, IGR). The broker's own flats are marked; nobody else's inventory is ever shown.
import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React, { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';

import { useSession } from '@/auth/session';
import { Card, Chip, ChipRow, ErrorBox, Loading, Notice, P, Row, Screen } from '@/ui/components';
import { usePalette } from '@/ui/theme';

const SOURCE: Record<string, string> = { tmc: 'TMC property-tax register', rera: 'MahaRERA', igr: 'IGR registrations', survey: 'field survey', ops: 'Only Broker team', broker: 'broker (unverified)' };

export default function SocietyStructureScreen() {
  const { id, wing: wingParam } = useLocalSearchParams<{ id: string; wing?: string }>();
  const { api } = useSession();
  const c = usePalette();
  const q = useQuery({ queryKey: ['structure', id], queryFn: () => api.societyStructure(id) });
  const [picked, setPicked] = useState<string | undefined>(wingParam);
  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (q.error || !q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const s = q.data;
  const wing = s.wings.find((w) => w.name === picked) ?? s.wings[0];
  const mineCount = s.wings.reduce((n, w) => n + w.floors.reduce((m, f) => m + f.flats.filter((x) => x.mine).length, 0), 0);

  return (
    <Screen>
      <Card>
        <P style={{ fontWeight: '700' }}>{s.society.name}</P>
        <P small muted>
          {s.society.locality} · {s.wings.length} wing{s.wings.length === 1 ? '' : 's'} · {s.wings.reduce((n, w) => n + w.flats_total, 0)} flats
          {s.sources.length ? ` · source: ${s.sources.map((x) => SOURCE[x] ?? x).join(', ')}` : ''}
        </P>
        {mineCount ? <P small>You handle {mineCount} flat{mineCount === 1 ? '' : 's'} here (marked).</P> : null}
      </Card>
      {s.wings.length > 1 ? (
        <ChipRow>{s.wings.map((w) => <Chip key={w.id} label={w.name} selected={w.id === wing?.id} onPress={() => setPicked(w.name)} />)}</ChipRow>
      ) : null}
      {!wing || !wing.known ? (
        <Notice tone="warn">We don’t have this building’s official flat list yet. It is being added from TMC and MahaRERA records.</Notice>
      ) : (
        <Card>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700' }}>{wing.name}</P>
            {wing.layout.register_complete ? <Chip label="Official list" tone="ok" /> : wing.layout.verified ? <Chip label="Verified layout" tone="ok" /> : <Chip label="Partly known" tone="warn" />}
          </Row>
          <P small muted>
            Floors {wing.layout.lowest_floor === 0 ? 'G' : wing.layout.lowest_floor}–{wing.layout.floors_total} · {wing.layout.units_per_floor} flats a floor
            {wing.layout.skip_floors.length ? ` · no flats on floor ${wing.layout.skip_floors.join(', ')}` : ''}
          </P>
          <ScrollView horizontal>
            <View style={{ gap: 3 }}>
              {wing.floors.map((f) => (
                <View key={f.label} style={{ flexDirection: 'row', alignItems: 'center', gap: 3, opacity: f.no_flats ? 0.55 : 1 }}>
                  <Text style={{ width: 52, textAlign: 'right', color: c.textMuted, fontSize: 11, paddingRight: 4 }}>{f.no_flats ? `${f.label} refuge` : f.label}</Text>
                  {f.flats.map((x) => (
                    <View
                      key={x.no}
                      testID={x.mine ? `mine-${x.no}` : undefined}
                      style={{
                        minWidth: 46, paddingVertical: 4, paddingHorizontal: 3, borderRadius: 5, borderWidth: 1, alignItems: 'center',
                        borderColor: x.mine ? c.brand : c.border, backgroundColor: x.mine ? c.brand : c.surface,
                      }}
                    >
                      <Text style={{ fontSize: 11, color: x.mine ? c.brandText : c.text, fontWeight: x.mine ? '700' : '400' }}>{x.no}</Text>
                    </View>
                  ))}
                </View>
              ))}
            </View>
          </ScrollView>
          <P small muted>Dark boxes are your flats. Other flats are shown as they exist in the building, not as available.</P>
        </Card>
      )}
    </Screen>
  );
}
