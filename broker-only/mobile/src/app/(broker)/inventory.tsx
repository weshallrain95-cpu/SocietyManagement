// My flats at scale (approved design, 2026-09-24; two lists 2026-09-25): "Available now" (the flats the broker is
// offering, picked by them) and "All flats" (everything they added). One search box for society, flat number, owner name or
// phone; filters; quick views with counts; sort; browse by society → wing. Only the broker's own flats.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router } from 'expo-router';
import React, { useState } from 'react';
import { Image, Linking, Platform, Pressable, ScrollView, Text, TextInput, View } from 'react-native';

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
  const qc = useQueryClient();
  const [list, setList] = useState<'available_now' | 'all'>('available_now');
  const [selecting, setSelecting] = useState(false);
  const [picked, setPicked] = useState<string[]>([]);
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
    list: list === 'available_now' ? 'available_now' : undefined,
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
  const filtered = !!(term || txn || bhks.length || budget || area || place || quick);
  const clearAll = () => {
    setQ(''); setTxn(''); setBhks([]); setBudget(0); setArea(null); setPlace(null); setQuick(undefined); setLimit(PAGE);
  };
  const toggle = (p: Panel) => setPanel(panel === p ? '' : p);
  const onList = list === 'available_now';
  const switchList = (to: 'available_now' | 'all') => { setList(to); setSelecting(false); setPicked([]); setLimit(PAGE); };
  const setAvail = useMutation({
    mutationFn: ({ ids, on }: { ids: string[]; on: boolean }) => api.setAvailableNow(ids, on),
    onSuccess: () => { setSelecting(false); setPicked([]); qc.invalidateQueries({ queryKey: ['listings'] }); },
  });
  const pick = (id: string) => setPicked(picked.includes(id) ? picked.filter((x) => x !== id) : [...picked, id]);
  const summary = [
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

      <View style={{ flexDirection: 'row', backgroundColor: c.surfaceAlt, borderRadius: 12, padding: 4 }} accessibilityRole="tablist">
        {([['available_now', 'Available now', d?.counts.available_now], ['all', 'All flats', d?.counts.total]] as const).map(([key, label, n]) => (
          <Pressable
            key={key}
            onPress={() => switchList(key)}
            accessibilityRole="tab"
            accessibilityState={{ selected: list === key }}
            style={{ flex: 1, alignItems: 'center', paddingVertical: 10, borderRadius: 9, backgroundColor: list === key ? c.surface : 'transparent', borderWidth: list === key ? 1 : 0, borderColor: c.border }}
            testID={`list-${key}`}
          >
            <Text style={{ fontSize: 15, fontWeight: '800', color: list === key ? c.text : c.textMuted }}>{label}{n !== undefined ? ` · ${n.toLocaleString('en-IN')}` : ''}</Text>
          </Pressable>
        ))}
      </View>

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
        <Chip label={txn === 'RENT' ? 'Rent' : txn ? 'Sale' : 'Rent / Sale'} selected={!!txn} onPress={() => setTxn(txn === '' ? 'RENT' : txn === 'RENT' ? 'SALE_RESALE,SALE_NEW' : '')} />
        <Chip label={bhks.length ? `${bhks.map((b) => (b >= 4 ? '4+' : b)).join(', ')} BHK ▾` : 'BHK ▾'} selected={!!bhks.length || panel === 'bhk'} onPress={() => toggle('bhk')} />
        <Chip label={budget ? `${BUDGETS[budget].label} ▾` : 'Budget ▾'} selected={!!budget || panel === 'budget'} onPress={() => toggle('budget')} />
        <Chip label={area ? `${area.name} ▾` : 'Area ▾'} selected={!!area || panel === 'area'} onPress={() => toggle('area')} />
        <Chip label="Sort ▾" selected={panel === 'sort'} onPress={() => toggle('sort')} />
      </ScrollView>
      {place ? (
        <Row>
          <Chip label={`${place.label}  ✕`} selected onPress={() => { setPlace(null); setLimit(PAGE); }} />
          <P small muted>Tap ✕ to show all flats</P>
        </Row>
      ) : null}

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
          {d && d.count > 0 ? (
            selecting ? (
              <Row style={{ justifyContent: 'space-between', backgroundColor: c.surface, borderRadius: 12, padding: 10, borderWidth: 1, borderColor: c.brand }}>
                <P style={{ fontWeight: '700' }}>{picked.length} picked</P>
                <Row>
                  <Button small kind="ghost" title="Cancel" onPress={() => { setSelecting(false); setPicked([]); }} />
                  <Button
                    small
                    kind={onList ? 'danger' : 'primary'}
                    title={onList ? `Remove ${picked.length} from Available now` : `Make ${picked.length} available now`}
                    disabled={!picked.length}
                    busy={setAvail.isPending}
                    onPress={() => setAvail.mutate({ ids: picked, on: !onList })}
                    testID="apply-available"
                  />
                </Row>
              </Row>
            ) : (
              <Button small kind="secondary" title={onList ? 'Select flats to remove from Available now' : 'Select flats to make available now'} onPress={() => setSelecting(true)} testID="select-flats" />
            )
          ) : null}
          {setAvail.error ? <ErrorBox error={setAvail.error} /> : null}
          {d && d.count === 0 && onList && !filtered ? (
            <Empty title="Your Available now list is empty" body="Pick the flats you are offering right now from All flats. Only these are matched to customers and shared." />
          ) : null}
          {d && d.count === 0 && onList && !filtered ? <Button title="Choose from All flats" onPress={() => switchList('all')} testID="go-all-flats" /> : null}
          {d && d.count === 0 && !(onList && !filtered) ? (
            term ? <Empty title={`No flat matches “${term}”`} body="Try the society’s short name, just the flat number, or the owner’s name or number. Only your own flats are searched." />
              : <Empty title="No flats here" body="Change the filters, or add a flat." />
          ) : null}
          {d?.results.map((l) => (
            <FlatCard
              key={l.id}
              l={l}
              showListTag={!onList}
              selecting={selecting}
              checked={picked.includes(l.id)}
              onPick={() => pick(l.id)}
              onMakeAvailable={() => setAvail.mutate({ ids: [l.id], on: true })}
            />
          ))}
          {d && d.results.length < d.count ? (
            <Button kind="secondary" title={`Show more (${d.count - d.results.length} left)`} onPress={() => setLimit(limit + PAGE)} busy={r.isFetching} />
          ) : null}
          <Button kind="ghost" title="📢 Share ready flats with fellow brokers" onPress={() => router.push('/trade/blast?kind=flats')} testID="open-trade-blast" />
        </>
      )}
    </Screen>
  );
}

function FlatCard({ l, showListTag, selecting, checked, onPick, onMakeAvailable }: {
  l: Listing; showListTag: boolean; selecting: boolean; checked: boolean; onPick: () => void; onMakeAvailable: () => void;
}) {
  const c = usePalette();
  const tone = statusTone(l.status);
  const toneBg = { ok: c.okBg, warn: c.warnBg, bad: c.badBg, info: c.infoBg }[tone];
  const toneFg = { ok: c.ok, warn: c.warn, bad: c.bad, info: c.info }[tone];
  const days = daysSince(l.last_confirmed_at);
  return (
    <Pressable
      onPress={selecting ? onPick : () => router.push(`/listing/${l.id}`)}
      accessibilityRole={selecting ? 'checkbox' : 'button'}
      accessibilityState={selecting ? { checked } : undefined}
      accessibilityLabel={`${l.society} ${l.building} flat ${l.unit_no}`}
      style={{ backgroundColor: c.surface, borderRadius: 14, padding: 10, flexDirection: 'row', gap: 12, borderWidth: checked ? 2 : 1, borderColor: checked ? c.brand : c.border }}
      testID={`flat-${l.unit_no}`}
    >
      {selecting ? (
        <View style={{ justifyContent: 'center' }}>
          <View style={{ width: 26, height: 26, borderRadius: 7, borderWidth: 2, borderColor: checked ? c.brand : c.border, backgroundColor: checked ? c.brand : c.surface, alignItems: 'center', justifyContent: 'center' }}>
            {checked ? <Text style={{ color: c.brandText, fontWeight: '800' }}>✓</Text> : null}
          </View>
        </View>
      ) : null}
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
          {showListTag && l.available_now ? <Text style={{ fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: c.okBg, color: c.ok, overflow: 'hidden' }}>✓ Available now</Text> : null}
          {showListTag && !l.available_now && !selecting && !l.owner_withdrew ? (
            <Pressable onPress={onMakeAvailable} accessibilityRole="button" accessibilityLabel={`Make ${l.society} ${l.unit_no} available now`} hitSlop={8} testID={`make-available-${l.unit_no}`}>
              <Text style={{ fontSize: 11, fontWeight: '800', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, borderWidth: 1, borderColor: c.brand, color: c.brand, overflow: 'hidden' }}>+ Make available now</Text>
            </Pressable>
          ) : null}
          {l.directions_url ? (
            <Pressable onPress={() => Linking.openURL(l.directions_url!)} accessibilityRole="link" accessibilityLabel={`Directions to ${l.society}`} hitSlop={8}>
              <Text style={{ fontSize: 11, fontWeight: '700', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 999, backgroundColor: c.surfaceAlt, color: c.brand, overflow: 'hidden' }}>📍 Directions</Text>
            </Pressable>
          ) : null}
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
