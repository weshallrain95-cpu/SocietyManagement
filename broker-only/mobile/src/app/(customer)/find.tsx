// Customer marketplace home (MKT-01, MKT-09): what's available around Thane West right now (counts and price
// bands only, never a broker's flat details), how many brokers are online, and the customer's own requests.
import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Text, View } from 'react-native';

import type { Locality, SupplyCluster } from '@/api';
import { useSession } from '@/auth/session';
import { ago, inr } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Empty, ErrorBox, H2, Loading, P, Row, Screen } from '@/ui/components';
import { usePalette } from '@/ui/theme';

export const ENQUIRY_STATE: Record<string, { label: string; tone: 'ok' | 'warn' | 'info' | 'bad' }> = {
  open: { label: 'Waiting for offers', tone: 'info' },
  in_progress: { label: 'Brokers accepted', tone: 'ok' },
  fulfilled: { label: 'Found a flat', tone: 'ok' },
  cancelled: { label: 'Cancelled', tone: 'bad' },
  expired: { label: 'Expired', tone: 'warn' },
};

type Area = { locality: Locality; units: number; brokers: number; p25: number | null; p75: number | null };

function byArea(clusters: SupplyCluster[], localities: Locality[]): Area[] {
  const out = new Map<string, Area>();
  for (const cl of clusters) {
    let best: Locality | null = null;
    let bestD = Infinity;
    for (const l of localities) {
      const d = (l.centroid.lat - cl.lat) ** 2 + (l.centroid.lng - cl.lng) ** 2;
      if (d < bestD) { best = l; bestD = d; }
    }
    if (!best) continue;
    const a = out.get(best.id) ?? { locality: best, units: 0, brokers: 0, p25: null, p75: null };
    a.units += cl.units;
    a.brokers = Math.max(a.brokers, cl.brokers_serving);
    if (cl.price_band) {
      a.p25 = a.p25 === null ? cl.price_band.p25 : Math.min(a.p25, cl.price_band.p25);
      a.p75 = a.p75 === null ? cl.price_band.p75 : Math.max(a.p75, cl.price_band.p75);
    }
    out.set(best.id, a);
  }
  return [...out.values()].sort((x, y) => y.units - x.units);
}

export default function Find() {
  const { api } = useSession();
  const c = usePalette();
  const [txn, setTxn] = useState<'RENT' | 'SALE_RESALE'>('RENT');
  const [bhk, setBhk] = useState<string | undefined>();
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities });
  const bbox = useMemo<[number, number, number, number] | null>(() => {
    const ls = localities.data;
    if (!ls?.length) return null;
    const lats = ls.map((l) => l.centroid.lat);
    const lngs = ls.map((l) => l.centroid.lng);
    return [Math.min(...lngs) - 0.02, Math.min(...lats) - 0.02, Math.max(...lngs) + 0.02, Math.max(...lats) + 0.02];
  }, [localities.data]);
  const supply = useQuery({
    queryKey: ['supply', txn, bhk, bbox],
    queryFn: () => api.supplyMap({ bbox: bbox!, zoom: 13, txn, bhk }),
    enabled: !!bbox,
  });
  const mine = useQuery({ queryKey: ['my-enquiries'], queryFn: api.myEnquiries });
  const areas = supply.data && localities.data ? byArea(supply.data.clusters, localities.data) : [];
  const total = areas.reduce((s, a) => s + a.units, 0);
  const rent = txn === 'RENT';

  return (
    <Screen onRefresh={() => { supply.refetch(); mine.refetch(); }} refreshing={supply.isFetching && !supply.isLoading}>
      <Card>
        <Text style={{ fontSize: 20, fontWeight: '800', color: c.text }}>Tell brokers what you need</Text>
        <P muted small>One request reaches every verified broker in the area. They reply with their terms; you pick up to 3. Your number stays hidden until you accept.</P>
        <Button title="Post my requirement" onPress={() => router.push('/enquiry/new')} testID="post-requirement" />
      </Card>

      {mine.data?.length ? (
        <>
          <H2>My requests</H2>
          {mine.data.map((e) => (
            <Card key={e.id} onPress={() => router.push(`/enquiry/${e.id}`)} testID={`enquiry-${e.id}`}>
              <P style={{ fontWeight: '700' }}>{e.summary}</P>
              <Row style={{ flexWrap: 'wrap' }}>
                <Chip label={ENQUIRY_STATE[e.state]?.label ?? e.state} tone={ENQUIRY_STATE[e.state]?.tone} />
                <Chip label={`${e.proposals} offer${e.proposals === 1 ? '' : 's'}`} tone={e.proposals ? 'ok' : undefined} />
                <P small muted>sent to {e.recipients} brokers · {ago(e.created_at)}</P>
              </Row>
            </Card>
          ))}
        </>
      ) : null}

      <H2>Available now in Thane West</H2>
      <ChipRow>
        <Chip label="Rent" selected={rent} onPress={() => setTxn('RENT')} />
        <Chip label="Buy" selected={!rent} onPress={() => setTxn('SALE_RESALE')} />
        {['1', '2', '3', '4+'].map((b) => (
          <Chip key={b} label={`${b} BHK`} selected={bhk === b} onPress={() => setBhk(bhk === b ? undefined : b)} />
        ))}
      </ChipRow>
      {supply.isLoading || localities.isLoading ? <Loading /> : null}
      {supply.error ? <ErrorBox error={supply.error} onRetry={supply.refetch} /> : null}
      {supply.data ? (
        <Row style={{ gap: 10 }}>
          <View style={{ flex: 1, backgroundColor: c.surface, borderRadius: 12, padding: 12, borderWidth: 1, borderColor: c.border }}>
            <Text style={{ fontSize: 22, fontWeight: '800', color: c.brand }}>{total}</Text>
            <P small muted>flats {rent ? 'for rent' : 'for sale'}</P>
          </View>
          <View style={{ flex: 1, backgroundColor: c.surface, borderRadius: 12, padding: 12, borderWidth: 1, borderColor: c.border }}>
            <Text style={{ fontSize: 22, fontWeight: '800', color: c.ok }}>{supply.data.brokers_online.length}</Text>
            <P small muted>brokers online</P>
          </View>
        </Row>
      ) : null}
      {supply.data && !areas.length ? <Empty title="Nothing listed here yet" body="Post your requirement anyway: brokers often have flats that are not listed yet." /> : null}
      {areas.map((a) => (
        <Card key={a.locality.id} onPress={() => router.push(`/enquiry/new?locality=${a.locality.id}&txn=${txn}`)}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{a.locality.name}</P>
            <Chip label={`${a.units} flat${a.units === 1 ? '' : 's'}`} tone="info" />
          </Row>
          <P small muted>
            {a.p25 !== null && a.p75 !== null ? `Usually ${inr(a.p25, rent)} – ${inr(a.p75, rent)}` : 'Price range shown once enough flats are listed'} · {a.brokers} broker{a.brokers === 1 ? '' : 's'} serving
          </P>
          <P small style={{ color: c.brand, fontWeight: '700' }}>Ask brokers here ›</P>
        </Card>
      ))}
      <P small muted>Only counts and price ranges are shown. Brokers share flat details once you accept their offer.</P>
    </Screen>
  );
}
