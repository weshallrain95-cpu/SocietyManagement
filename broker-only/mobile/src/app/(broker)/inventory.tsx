// My flats at scale (approved design, 2026-09-24): one search box for society, flat number, owner name or
// phone; filters; quick views with counts; sort; browse by society → wing. Only the broker's own flats.
import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';
import { Image, Platform, Pressable, ScrollView, Text, TextInput, View } from 'react-native';

import type { BrowseParams, Listing, QuickView } from '@/api';
import { useSession } from '@/auth/session';
import { bhk, daysSince, inr, statusTone } from '@/lib/format';
import { useDebounced } from '@/lib/useDebounced';
import { Button, Chip, ChipRow, Empty, ErrorBox, Loading, P, Row, Screen } from '@/ui/components';
import { usePalette } from '@/ui/theme';

type Panel = '' | 'bhk' | 'budget' | 'area' | 'sort';
const QUICK: { key: QuickView; label: string; tone: 'warn' | 'info' | 'bad' }[] = [
  { key: 'reconfirm', label: 'Reconfirm due', tone: 'warn' },
  { key: 'new', label: 'New this week', tone: 'info' },
  { key: 'keys_office', label: 'Keys at office', tone: 'info' },
  { key: 'no_photos', label: 'No photos yet', tone: 'bad' },
];
const BUDGETS: { label: string; min?: number; max?: number }[] = [
  { label: 'Any' }, { label: 'Up to ₹15k', max: 15000 }, { label: '₹15k–25k', min: 15000, max: 25000 },
  { label: '₹25k–40k', min: 25000, max: 40000 }, { label: '₹40k+', min: 40000 },
];
const SORTS: { key: NonNullable<BrowseParams['sort']>; label: string }[] = [
  { key: 'confirmed', label: 'Last confirmed' }, { key: 'newest', label: 'Newest' },
  { key: 'price_low', label: 'Price: low to high' }, { key: 'price_high', label: 'Price: high to low' },
];
const PAGE = 40;
// The box's own border shows focus; drop the browser's extra focus ring on the web build.
const NO_OUTLINE = (Platform.OS === 'web' ? { outlineStyle: 'none' } : {}) as object;

export default function Inventory() {
  const { api } = useSession();
  const c = usePalette();
  const [q, setQ] = useState('');
  const term = useDebounced(q.trim(), 300);
  const [available, setAvailable] = useState(true);
  const [txn, setTxn] = useState<'' | 'RENT' | 'SALE_RESALE,SALE_NEW'>('');
  const [bhks, setBhks] = useState<number[]>([]);
  const [budget, setBudget] = useState(0);
  const [area, setArea] = useState<{ id: string; name: string } | null>(null);
  const [place, setPlace] = useState<{ society_id?: string; building_id?: string; label: string } | null>(null);
  const [quick, setQuick] = useState<QuickView | undefined>();
  const [sort, setSort] = useState<NonNullable<BrowseParams['sort']>>('confirmed');
  const [panel, setPanel] = useState<Panel>('');
  const [mode, setMode] = useState<'list' | 'society'>('list');
  const [limit, setLimit] = useState(PAGE);

  const params: BrowseParams = {
    q: term || undefined,
    status: available ? 'AVAILABLE,AVAILABLE_UNCONFIRMED' : undefined,
    txn_type: txn || undefined,
    bhk: bhks.length ? bhks.join(',') : undefined,
    price_min: BUDGETS[budget].min,
    price_max: BUDGETS[budget].max,
    locality_id: area?.id,
    society_id: place?.society_id,
    building_id: place?.building_id,
    quick,
    sort,
    limit,
  };
  const r = useQuery({ queryKey: ['listings', 'browse', params], queryFn: () => api.browseListings(params), placeholderData: (prev) => prev });
  const tree = useQuery({ queryKey: ['listings', 'by-society'], queryFn: api.listingsBySociety, enabled: mode === 'society' });
  const localities = useQuery({ queryKey: ['localities'], queryFn: api.localities, enabled: panel === 'area' });
  const d = r.data;
  const filtered = !!(term || !available || txn || bhks.length || budget || area || place || quick);
  const clearAll = () => {
    setQ(''); setAvailable(true); setTxn(''); setBhks([]); setBudget(0); setArea(null); setPlace(null); setQuick(undefined); setLimit(PAGE);
  };
  const toggle = (p: Panel) => setPanel(panel === p ? '' : p);
  const summary = [
    available ? 'available' : 'all statuses',
    txn === 'RENT' ? 'for rent' : txn ? 'for sale' : '',
    bhks.length ? `${bhks.map((b) => (b >= 4 ? '4+' : b)).join('/')} BHK` : '',
    budget ? BUDGETS[budget].label : '',
    area ? `in ${area.name}` : place ? `in ${place.label}` : '',
  ].filter(Boolean).join(' · ');

  return (
    <Screen onRefresh={r.refetch} refreshing={r.isFetching && !r.isLoading}>
      <Row style={{ justifyContent: 'space-between' }}>
        <Text style={{ fontSize: 22, fontWeight: '800', color: c.text }}>
          My flats <Text style={{ color: c.textMuted }}>{d ? d.counts.total.toLocaleString('en-IN') : ''}</Text>
        </Text>
        <Button small title="+ Add flat" onPress={() => router.push('/listing/new')} testID="add-flat" />
      </Row>

      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: c.surfaceAlt, borderRadius: 12, paddingHorizontal: 12, minHeight: 48, borderWidth: term ? 2 : 0, borderColor: c.brand }}>
        <Text style={{ fontSize: 18, color: c.textMuted }}>⌕</Text>
        <TextInput
          value={q}
          onChangeText={(t) => { setQ(t); setLimit(PAGE); }}
          placeholder="Society, flat no., owner name or phone"
          placeholderTextColor={c.textMuted}
          autoCorrect={false}
          autoCapitalize="none"
          style={[{ flex: 1, fontSize: 16, color: c.text, paddingVertical: 10 }, NO_OUTLINE]}
          accessibilityLabel="Search my flats"
          testID="flats-search"
        />
        {q ? <Pressable onPress={() => setQ('')} accessibilityRole="button" accessibilityLabel="Clear search" style={{ padding: 6 }}><Text style={{ color: c.textMuted, fontWeight: '700' }}>Clear</Text></Pressable> : null}
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6 }}>
        <Chip label="Available" selected={available} onPress={() => setAvailable(!available)} />
        <Chip label={txn === 'RENT' ? 'Rent' : txn ? 'Sale' : 'Rent / Sale'} selected={!!txn} onPress={() => setTxn(txn === '' ? 'RENT' : txn === 'RENT' ? 'SALE_RESALE,SALE_NEW' : '')} />
        <Chip label={bhks.length ? `${bhks.map((b) => (b >= 4 ? '4+' : b)).join(', ')} BHK ▾` : 'BHK ▾'} selected={!!bhks.length || panel === 'bhk'} onPress={() => toggle('bhk')} />
        <Chip label={budget ? `${BUDGETS[budget].label} ▾` : 'Budget ▾'} selected={!!budget || panel === 'budget'} onPress={() => toggle('budget')} />
        <Chip label={area ? `${area.name} ▾` : 'Area ▾'} selected={!!area || panel === 'area'} onPress={() => toggle('area')} />
        <Chip label="Sort ▾" selected={panel === 'sort'} onPress={() => toggle('sort')} />
      </ScrollView>

      {panel === 'bhk' ? (
        <ChipRow>
          {[0.5, 1, 2, 3, 4].map((b) => (
            <Chip key={b} label={b === 0.5 ? '1 RK' : b >= 4 ? '4+ BHK' : `${b} BHK`} selected={bhks.includes(b)} onPress={() => setBhks(bhks.includes(b) ? bhks.filter((x) => x !== b) : [...bhks, b])} />
          ))}
        </ChipRow>
      ) : null}
      {panel === 'budget' ? (
        <ChipRow>{BUDGETS.map((b, i) => <Chip key={b.label} label={b.label} selected={budget === i} onPress={() => { setBudget(i); setPanel(''); }} />)}</ChipRow>
      ) : null}
      {panel === 'area' ? (
        <ChipRow>
          <Chip label="Any area" selected={!area} onPress={() => { setArea(null); setPanel(''); }} />
          {localities.data?.map((l) => <Chip key={l.id} label={l.name} selected={area?.id === l.id} onPress={() => { setArea({ id: l.id, name: l.name }); setPlace(null); setPanel(''); }} />)}
        </ChipRow>
      ) : null}
      {panel === 'sort' ? (
        <ChipRow>{SORTS.map((s) => <Chip key={s.key} label={s.label} selected={sort === s.key} onPress={() => { setSort(s.key); setPanel(''); }} />)}</ChipRow>
      ) : null}

      {!term ? (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8 }}>
          {QUICK.map((v) => {
            const on = quick === v.key;
            const n = d?.counts[v.key];
            return (
              <Pressable
                key={v.key}
                onPress={() => { setQuick(on ? undefined : v.key); setLimit(PAGE); }}
                accessibilityRole="button"
                accessibilityState={{ selected: on }}
                style={{ backgroundColor: on ? c.brand : c.surface, borderRadius: 12, paddingVertical: 10, paddingHorizontal: 12, minWidth: 112, borderWidth: 1, borderColor: on ? c.brand : c.border }}
                testID={`quick-${v.key}`}
              >
                <Text style={{ fontSize: 18, fontWeight: '800', color: on ? c.brandText : { warn: c.warn, info: c.brand, bad: c.bad }[v.tone] }}>{n ?? '–'}</Text>
                <Text style={{ fontSize: 12, fontWeight: '600', color: on ? c.brandText : c.textMuted }}>{v.label}</Text>
              </Pressable>
            );
          })}
        </ScrollView>
      ) : null}

      <Row style={{ justifyContent: 'space-between' }}>
        <ChipRow>
          <Chip label="List" selected={mode === 'list'} onPress={() => setMode('list')} />
          <Chip label="By society" selected={mode === 'society'} onPress={() => setMode('society')} />
        </ChipRow>
        {filtered ? <Pressable onPress={clearAll} accessibilityRole="button"><Text style={{ color: c.brand, fontWeight: '700' }}>Clear all</Text></Pressable> : null}
      </Row>

      {mode === 'society' ? (
        <SocietyTree data={tree.data} loading={tree.isLoading} onPick={(p) => { setPlace(p); setArea(null); setMode('list'); setLimit(PAGE); }} />
      ) : (
        <>
          {d ? (
            <P small muted>
              {term ? `${d.count} of your flats match “${term}”` : `Showing ${d.count.toLocaleString('en-IN')}${summary ? ` · ${summary}` : ''}`}
              {quick ? ` · ${QUICK.find((x) => x.key === quick)?.label.toLowerCase()}` : ''} · sorted by {SORTS.find((s) => s.key === sort)?.label.toLowerCase()}
            </P>
          ) : null}
          {r.isLoading ? <Loading /> : r.error ? <ErrorBox error={r.error} onRetry={r.refetch} /> : null}
          {d && d.count === 0 ? (
            term ? <Empty title={`No flat matches “${term}”`} body="Try the society’s short name, just the flat number, or the owner’s name or number. Only your own flats are searched." />
              : <Empty title="No flats here" body="Change the filters, or add a flat." />
          ) : null}
          {d?.results.map((l) => <FlatCard key={l.id} l={l} />)}
          {d && d.results.length < d.count ? (
            <Button kind="secondary" title={`Show more (${d.count - d.results.length} left)`} onPress={() => setLimit(limit + PAGE)} busy={r.isFetching} />
          ) : null}
          <Button kind="ghost" title="📢 Share ready flats with fellow brokers" onPress={() => router.push('/trade/blast?kind=flats')} testID="open-trade-blast" />
        </>
      )}
    </Screen>
  );
}

function FlatCard({ l }: { l: Listing }) {
  const c = usePalette();
  const tone = statusTone(l.status);
  const toneBg = { ok: c.okBg, warn: c.warnBg, bad: c.badBg, info: c.infoBg }[tone];
  const toneFg = { ok: c.ok, warn: c.warn, bad: c.bad, info: c.info }[tone];
  const days = daysSince(l.last_confirmed_at);
  return (
    <Pressable
      onPress={() => router.push(`/listing/${l.id}`)}
      accessibilityRole="button"
      accessibilityLabel={`${l.society} ${l.building} flat ${l.unit_no}`}
      style={{ backgroundColor: c.surface, borderRadius: 14, padding: 10, flexDirection: 'row', gap: 12, borderWidth: 1, borderColor: c.border }}
      testID={`flat-${l.unit_no}`}
    >
      <View style={{ width: 84, height: 84, borderRadius: 10, backgroundColor: c.surfaceAlt, overflow: 'hidden', justifyContent: 'flex-end' }}>
        {l.thumb_url ? <Image source={{ uri: l.thumb_url }} style={{ position: 'absolute', width: 84, height: 84 }} /> : (
          <View style={{ position: 'absolute', width: 84, height: 84, alignItems: 'center', justifyContent: 'center' }}>
            <Text style={{ fontSize: 22, fontWeight: '800', color: c.textMuted }}>{bhk(l.bhk).replace(' BHK', '')}</Text>
            <Text style={{ fontSize: 10, color: c.textMuted, fontWeight: '700' }}>BHK</Text>
          </View>
        )}
        <Text style={{ margin: 5, alignSelf: 'flex-start', fontSize: 10.5, fontWeight: '700', color: '#FFFFFF', backgroundColor: 'rgba(21,32,31,0.72)', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 6, overflow: 'hidden' }}>
          {l.photo_count ? `${l.photo_count} photo${l.photo_count > 1 ? 's' : ''}${l.has_video ? ' + video' : ''}` : 'No photo'}
        </Text>
      </View>
      <View style={{ flex: 1, gap: 3, minWidth: 0 }}>
        <Row style={{ justifyContent: 'space-between' }}>
          <Text style={{ fontSize: 16, fontWeight: '800', color: c.brand }}>{inr(l.asking_rent ?? l.asking_price, l.txn_type === 'RENT')}</Text>
          <Text style={{ fontSize: 13, fontWeight: '700', color: c.text }}>{bhk(l.bhk)}</Text>
        </Row>
        <Text numberOfLines={1} style={{ fontSize: 14, fontWeight: '700', color: c.text }}>{l.society}</Text>
        <Text numberOfLines={1} style={{ fontSize: 12.5, color: c.textMuted }}>
          {l.building} · {l.unit_no}{l.floor !== null ? ` · Floor ${l.floor}` : ''}{l.carpet_sqft ? ` · ${l.carpet_sqft} sq ft` : ''}{l.owner_name ? ` · ${l.owner_name}` : ''}
        </Text>
        <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 2 }}>
          <Text style={{ fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: l.stale ? c.warnBg : toneBg, color: l.stale ? c.warn : toneFg, overflow: 'hidden' }}>
            {l.stale ? `Reconfirm · ${days} d` : `${l.status_label.replace(' – not yet confirmed by owner', ' (unconfirmed)')} · ${days} d`}
          </Text>
          {l.keys_holder === 'office' ? <Text style={{ fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: c.surfaceAlt, color: c.textMuted, overflow: 'hidden' }}>Keys at office</Text> : null}
          {l.owner_withdrew ? <Text style={{ fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: c.badBg, color: c.bad, overflow: 'hidden' }}>Owner removed you</Text> : null}
        </View>
      </View>
    </Pressable>
  );
}

function SocietyTree({ data, loading, onPick }: {
  data?: { society_id: string; name: string; count: number; wings: { building_id: string; name: string; count: number }[] }[];
  loading: boolean;
  onPick: (p: { society_id?: string; building_id?: string; label: string }) => void;
}) {
  const c = usePalette();
  const [open, setOpen] = useState<string | null>(null);
  if (loading) return <Loading />;
  if (!data?.length) return <Empty title="No flats yet" />;
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: 14, borderWidth: 1, borderColor: c.border, overflow: 'hidden' }}>
      {data.map((s) => (
        <View key={s.society_id} style={{ borderBottomWidth: 1, borderBottomColor: c.border }}>
          <Pressable onPress={() => setOpen(open === s.society_id ? null : s.society_id)} accessibilityRole="button" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 14, minHeight: 48 }}>
            <Text style={{ fontSize: 15, fontWeight: '800', color: c.text, flexShrink: 1 }}>{open === s.society_id ? '▾' : '▸'} {s.name}</Text>
            <Text style={{ fontSize: 13, fontWeight: '700', color: c.textMuted }}>{s.count} flat{s.count === 1 ? '' : 's'}</Text>
          </Pressable>
          {open === s.society_id ? (
            <View style={{ paddingBottom: 8 }}>
              <Pressable onPress={() => onPick({ society_id: s.society_id, label: s.name })} accessibilityRole="button" style={{ paddingVertical: 10, paddingHorizontal: 34 }}>
                <Text style={{ color: c.brand, fontWeight: '700' }}>All of {s.name}</Text>
              </Pressable>
              {s.wings.map((w) => (
                <Pressable key={w.building_id} onPress={() => onPick({ building_id: w.building_id, label: `${s.name}, ${w.name}` })} accessibilityRole="button" style={{ flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 10, paddingHorizontal: 34 }}>
                  <Text style={{ color: c.text, fontWeight: '600' }}>{w.name}</Text>
                  <Text style={{ color: c.textMuted, fontWeight: '700' }}>{w.count}</Text>
                </Pressable>
              ))}
            </View>
          ) : null}
        </View>
      ))}
    </View>
  );
}
