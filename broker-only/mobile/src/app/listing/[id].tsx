// The flat page (approved design, 2026-09-24): photos first, price and status, quick actions, customers who
// fit, key facts, house rules, what's in the flat and the society, distances, the building, the private
// block (owner, keys, brokerage, notes) and activity. "What customers see" hides everything private,
// including the flat number and wing.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import React, { useRef, useState } from 'react';
import { Alert, Image, Linking, Platform, Pressable, ScrollView, Text, TextInput, View, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { Listing, MediaItem, UploadFile } from '@/api';
import { useSession } from '@/auth/session';
import { ago, bhk, inr, phone, statusTone } from '@/lib/format';
import { canUseCamera, pickFromGallery, takePhoto } from '@/lib/pickMedia';
import { useDebounced } from '@/lib/useDebounced';
import { Button, Chip, ErrorBox, Field, Loading, Notice, P, Row } from '@/ui/components';
import { usePalette } from '@/ui/theme';

const KEY_LABEL: Record<string, string> = { office: 'At your office', owner: 'With the owner', staff: 'With field staff', society_office: 'Society office', lockbox: 'Lock-box', neighbour: 'With a neighbour' };
type View_ = 'broker' | 'customer';
type Picker = '' | 'share' | 'visit';
// The border already shows focus; drop the browser's extra focus ring on the web build.
const NO_OUTLINE = (Platform.OS === 'web' ? { outlineStyle: 'none' } : {}) as object;

function confirm(msg: string, ok: () => void) {
  if (Platform.OS === 'web') {
    if (globalThis.confirm?.(msg) ?? true) ok();
    return;
  }
  Alert.alert('Please confirm', msg, [{ text: 'Cancel', style: 'cancel' }, { text: 'Yes', onPress: ok }]);
}

export default function ListingDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const c = usePalette();
  const q = useQuery({ queryKey: ['listing', id], queryFn: () => api.listing(id) });
  const [view, setView] = useState<View_>('broker');
  const [picker, setPicker] = useState<Picker>('');
  const [showStatus, setShowStatus] = useState(false);
  const scroller = useRef<ScrollView>(null);
  // From the bottom bar, bring the customer list into view (it sits under the quick actions).
  const openPicker = (m: Picker) => {
    setPicker(m);
    scroller.current?.scrollTo({ y: 360, animated: true });
  };

  if (q.isLoading) return <View style={{ flex: 1, backgroundColor: c.bg, padding: 16 }}><Loading /></View>;
  if (q.error || !q.data) return <View style={{ flex: 1, backgroundColor: c.bg, padding: 16 }}><ErrorBox error={q.error} onRetry={q.refetch} /></View>;
  const l = q.data;
  const p = l.page;
  const broker = view === 'broker';
  const rent = l.txn_type === 'RENT';
  const floorText = l.floor === null ? '' : `Floor ${l.floor === 0 ? 'G' : l.floor}${p?.building.floors_total ? ` of ${p.building.floors_total}` : ''}`;
  const place = [p?.locality || l.locality, 'Thane West'].filter(Boolean).join(', ');
  const tone = statusTone(l.status);

  return (
    <SafeAreaView edges={['bottom']} style={{ flex: 1, backgroundColor: c.bg }}>
      <ScrollView ref={scroller} contentContainerStyle={{ paddingBottom: 110 }}>
        <View style={{ flexDirection: 'row', justifyContent: 'center', padding: 8, backgroundColor: c.surface }}>
          <View style={{ flexDirection: 'row', backgroundColor: c.surfaceAlt, borderRadius: 999, padding: 3 }}>
            {(['broker', 'customer'] as View_[]).map((v) => (
              <Pressable key={v} onPress={() => setView(v)} accessibilityRole="button" accessibilityState={{ selected: view === v }} style={{ paddingVertical: 7, paddingHorizontal: 14, borderRadius: 999, backgroundColor: view === v ? c.brand : 'transparent' }} testID={`view-${v}`}>
                <Text style={{ fontSize: 12.5, fontWeight: '700', color: view === v ? c.brandText : c.textMuted }}>{v === 'broker' ? 'Broker view' : 'What customers see'}</Text>
              </Pressable>
            ))}
          </View>
        </View>

        <Gallery l={l} broker={broker} onChange={() => q.refetch()} />

        <View style={{ backgroundColor: c.surface, padding: 16, gap: 6, borderBottomWidth: 1, borderBottomColor: c.border }}>
          <Text style={{ fontSize: 28, fontWeight: '800', color: c.brand }}>
            {inr(l.asking_rent ?? l.asking_price)}<Text style={{ fontSize: 14, color: c.textMuted, fontWeight: '600' }}>{rent ? ' /month' : ''}{l.negotiable ? ' · negotiable' : ''}</Text>
          </Text>
          {l.deposit || l.maintenance ? (
            <Text style={{ fontSize: 13, color: c.textMuted }}>{[l.deposit ? `Deposit ${inr(l.deposit)}` : '', l.maintenance ? `Maintenance ${inr(l.maintenance)}` : ''].filter(Boolean).join(' · ')}</Text>
          ) : null}
          <Text style={{ fontSize: 19, fontWeight: '800', color: c.text, marginTop: 4 }}>{bhk(l.bhk)} in {l.society}</Text>
          <Text style={{ fontSize: 14, color: c.textMuted }}>
            {broker ? [`${l.building} · Flat ${l.unit_no}`, floorText, place].filter(Boolean).join(' · ') : [floorText, place].filter(Boolean).join(' · ')}
          </Text>
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 4 }}>
            <Chip label={`${l.status_label} · confirmed ${ago(l.last_confirmed_at)}`} tone={tone} />
            {broker && l.owner_appointed ? <Chip label="Owner-appointed" tone="info" /> : null}
            {broker && l.keys ? <Chip label={`Keys: ${(KEY_LABEL[l.keys.holder_type] ?? l.keys.holder_type).toLowerCase()}`} /> : null}
            {broker && l.stale ? <Chip label="Reconfirm with the owner" tone="warn" /> : null}
          </View>
        </View>

        {broker && l.owner_withdrew ? <OwnerWithdrew id={id} /> : null}

        {broker ? (
          <View style={{ flexDirection: 'row', backgroundColor: c.surface, paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: c.border }}>
            <Action icon="☎" label="Call owner" primary disabled={!l.owner_phone || l.owner_phone.includes('•')} onPress={() => Linking.openURL(`tel:${(l.owner_phone ?? '').replace(/[^\d+]/g, '')}`)} />
            <Action icon="↗" label="Share" onPress={() => setPicker(picker === 'share' ? '' : 'share')} />
            <Action icon="▦" label="Add to visit" onPress={() => setPicker(picker === 'visit' ? '' : 'visit')} />
            <Action icon="↻" label="Status" onPress={() => setShowStatus(!showStatus)} testID="open-status" />
          </View>
        ) : null}

        <View style={{ padding: 12, gap: 12 }}>
          {broker && picker ? <CustomerPicker l={l} mode={picker} onDone={() => setPicker('')} /> : null}
          {broker && showStatus ? <StatusPanel l={l} onDone={() => { setShowStatus(false); q.refetch(); }} /> : null}

          {broker && p && p.fitting_customers.count > 0 ? (
            <Pressable onPress={() => openPicker('share')} accessibilityRole="button" style={{ backgroundColor: c.brand, borderRadius: 14, padding: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }} testID="fitting-customers">
              <View style={{ flexShrink: 1, gap: 2 }}>
                <Text style={{ color: c.brandText, fontSize: 15, fontWeight: '800' }}>{p.fitting_customers.count} of your customers fit this flat</Text>
                <Text style={{ color: c.brandText, opacity: 0.85, fontSize: 12.5 }}>
                  {p.fitting_customers.customers.map((x) => x.name).join(', ')}{p.fitting_customers.count > p.fitting_customers.customers.length ? ` and ${p.fitting_customers.count - p.fitting_customers.customers.length} more` : ''} · budget, BHK and area fit
                </Text>
              </View>
              <Text style={{ color: c.brandText, fontSize: 20, fontWeight: '800' }}>›</Text>
            </Pressable>
          ) : null}

          {p ? (
            <>
              <Section title="Key facts">
                <View style={{ flexDirection: 'row', flexWrap: 'wrap', rowGap: 14 }}>
                  {p.facts.map((f) => (
                    <View key={f.label} style={{ width: '50%', paddingRight: 8, gap: 2 }}>
                      <Text style={{ fontSize: 11.5, fontWeight: '600', color: c.textMuted, letterSpacing: 0.3, textTransform: 'uppercase' }}>{f.label}</Text>
                      <Text style={{ fontSize: 14.5, fontWeight: '700', color: c.text }}>{f.value}{f.disputed ? ' (disputed)' : ''}</Text>
                    </View>
                  ))}
                </View>
                {p.facts.length < 5 ? <P small muted>More details appear as the owner, you and site visits fill them in.</P> : null}
              </Section>

              {p.house_rules.length ? (
                <Section title="House rules (owner)">
                  {p.house_rules.map((r) => (
                    <Row key={r.label} style={{ justifyContent: 'space-between' }}>
                      <Text style={{ fontSize: 14, color: c.textMuted, flexShrink: 1 }}>{r.label}</Text>
                      <Text style={{ fontSize: 14, fontWeight: '700', color: { ok: c.ok, warn: c.warn, bad: c.bad }[r.tone] }}>{r.value}</Text>
                    </Row>
                  ))}
                </Section>
              ) : null}

              {p.in_flat.length || p.society_amenities.length ? (
                <Section title={p.in_flat.length ? 'In the flat' : 'In the society'}>
                  {p.in_flat.length ? <Tags items={p.in_flat} /> : null}
                  {p.in_flat.length && p.society_amenities.length ? <Text style={{ fontSize: 16, fontWeight: '800', color: c.text, marginTop: 6 }}>In the society</Text> : null}
                  {p.society_amenities.length ? <Tags items={p.society_amenities} /> : null}
                </Section>
              ) : null}

              <Section title="Location and distances">
                {p.location ? (
                  <Pressable onPress={() => Linking.openURL(`https://www.google.com/maps/search/?api=1&query=${p.location!.lat},${p.location!.lng}`)} accessibilityRole="link" style={{ height: 110, borderRadius: 10, backgroundColor: c.surfaceAlt, alignItems: 'center', justifyContent: 'center', gap: 4 }}>
                    <Text style={{ fontSize: 13, fontWeight: '700', color: c.text }}>{l.society}{broker ? ` · ${l.building}` : ''}</Text>
                    <Text style={{ fontSize: 12.5, fontWeight: '700', color: c.brand }}>Open in Google Maps ›</Text>
                  </Pressable>
                ) : null}
                {p.places.length ? p.places.map((x) => (
                  <Row key={x.label} style={{ justifyContent: 'space-between' }}>
                    <Text style={{ fontSize: 14, color: c.textMuted, flexShrink: 1 }}>{x.label}</Text>
                    <Text style={{ fontSize: 14, fontWeight: '700', color: c.text }}>{x.value}</Text>
                  </Row>
                )) : <P small muted>Distances are worked out from the map pin once the building is placed.</P>}
              </Section>

              {broker ? (
                <Pressable onPress={() => router.push(`/society/${l.society_id}?wing=${encodeURIComponent(l.building)}`)} accessibilityRole="button" style={{ backgroundColor: c.surface, borderRadius: 14, padding: 16, flexDirection: 'row', alignItems: 'center', gap: 14, borderWidth: 1, borderColor: c.border }} testID="open-structure">
                  <View style={{ width: 56, flexDirection: 'row', flexWrap: 'wrap', gap: 2 }}>
                    {Array.from({ length: 16 }, (_, i) => <View key={i} style={{ width: 12, height: 8, borderRadius: 2, backgroundColor: i === 6 ? c.brand : c.border }} />)}
                  </View>
                  <View style={{ flex: 1, gap: 2 }}>
                    <Text style={{ fontSize: 15, fontWeight: '800', color: c.text }}>See the building, floor by floor</Text>
                    <Text style={{ fontSize: 12.5, color: c.textMuted }}>
                      {[l.building, p.building.floors_total ? `${p.building.floors_total} floors` : '', p.building.units_per_floor ? `${p.building.units_per_floor} flats a floor` : '', p.building.official_list ? 'official list' : ''].filter(Boolean).join(' · ')}
                    </Text>
                  </View>
                  <Text style={{ color: c.brand, fontSize: 20, fontWeight: '800' }}>›</Text>
                </Pressable>
              ) : null}

              {broker ? (
                <View style={{ backgroundColor: c.surface, borderRadius: 14, padding: 16, gap: 12, borderWidth: 1.5, borderStyle: 'dashed', borderColor: c.border }}>
                  <Text style={{ fontSize: 16, fontWeight: '800', color: c.text }}>Only your firm sees this</Text>
                  <Private label="Owner" value={[l.owner_name || 'Not recorded', l.owner_phone ? phone(l.owner_phone) : ''].filter(Boolean).join(' · ')} note={p.owner_on_platform ? 'Registered on Only Broker' : undefined} />
                  <Private label="Keys" value={l.keys ? `${KEY_LABEL[l.keys.holder_type] ?? l.keys.holder_type}${l.keys.instructions ? ` · ${l.keys.instructions}` : ''}` : 'Not recorded'} note="Field staff see this only on the day of a visit" />
                  <Private label="Brokerage" value={l.brokerage_terms || 'Not recorded'} />
                  {l.private_notes ? <Private label="Private notes" value={l.private_notes} /> : null}
                  {p.other_brokers !== null ? <Private label="Also listed by" value={p.other_brokers ? `${p.other_brokers} other broker${p.other_brokers > 1 ? 's' : ''} (names never shown)` : 'No other broker on Only Broker'} /> : null}
                </View>
              ) : null}

              {broker && p.activity.length ? (
                <Section title="Activity">
                  {p.activity.map((a, i) => (
                    <View key={i} style={{ flexDirection: 'row', gap: 10 }}>
                      <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: c.brand, marginTop: 6 }} />
                      <View style={{ flex: 1 }}>
                        <Text style={{ fontSize: 14, fontWeight: '600', color: c.text }}>{a.text}</Text>
                        <Text style={{ fontSize: 12, color: c.textMuted }}>{ago(a.at)}</Text>
                      </View>
                    </View>
                  ))}
                </Section>
              ) : null}

              {!broker ? <Notice>This is what a customer sees on the link you share: no flat number, wing, owner or keys.</Notice> : null}
            </>
          ) : null}
        </View>
      </ScrollView>

      {broker ? (
        <View style={{ position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: c.surface, borderTopWidth: 1, borderTopColor: c.border, padding: 12, paddingBottom: 20, flexDirection: 'row', gap: 8 }}>
          <BarButton label="Share with customer" onPress={() => openPicker('share')} testID="share-with-customer" />
          <BarButton label="Plan a visit" primary onPress={() => openPicker('visit')} testID="plan-visit" />
        </View>
      ) : null}
    </SafeAreaView>
  );
}

function BarButton({ label, onPress, primary, testID }: { label: string; onPress: () => void; primary?: boolean; testID?: string }) {
  const c = usePalette();
  return (
    <Pressable onPress={onPress} accessibilityRole="button" testID={testID} style={{ flex: 1, height: 48, borderRadius: 12, alignItems: 'center', justifyContent: 'center', backgroundColor: primary ? c.brand : c.surface, borderWidth: 1.5, borderColor: c.brand }}>
      <Text numberOfLines={1} style={{ fontSize: 15, fontWeight: '800', color: primary ? c.brandText : c.brand }}>{label}</Text>
    </Pressable>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  const c = usePalette();
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: 14, padding: 16, gap: 10, borderWidth: 1, borderColor: c.border }}>
      <Text style={{ fontSize: 16, fontWeight: '800', color: c.text }}>{title}</Text>
      {children}
    </View>
  );
}

function Tags({ items }: { items: string[] }) {
  const c = usePalette();
  return (
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 6 }}>
      {items.map((t) => <Text key={t} style={{ fontSize: 12.5, fontWeight: '600', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8, backgroundColor: c.surfaceAlt, color: c.text, overflow: 'hidden' }}>{t}</Text>)}
    </View>
  );
}

function Private({ label, value, note }: { label: string; value: string; note?: string }) {
  const c = usePalette();
  return (
    <View style={{ gap: 2 }}>
      <Text style={{ fontSize: 11.5, fontWeight: '600', color: c.textMuted, letterSpacing: 0.3, textTransform: 'uppercase' }}>{label}</Text>
      <Text style={{ fontSize: 14.5, fontWeight: '700', color: c.text }}>{value}</Text>
      {note ? <Text style={{ fontSize: 12, color: c.textMuted }}>{note}</Text> : null}
    </View>
  );
}

function Action({ icon, label, onPress, primary, disabled, testID }: { icon: string; label: string; onPress: () => void; primary?: boolean; disabled?: boolean; testID?: string }) {
  const c = usePalette();
  return (
    <Pressable onPress={onPress} disabled={disabled} accessibilityRole="button" accessibilityLabel={label} style={{ flex: 1, alignItems: 'center', gap: 6, opacity: disabled ? 0.4 : 1, minHeight: 64 }} testID={testID}>
      <View style={{ width: 42, height: 42, borderRadius: 12, backgroundColor: primary ? c.brand : c.surfaceAlt, alignItems: 'center', justifyContent: 'center' }}>
        <Text style={{ fontSize: 18, color: primary ? c.brandText : c.brand, fontWeight: '800' }}>{icon}</Text>
      </View>
      <Text style={{ fontSize: 11.5, fontWeight: '700', color: c.text }}>{label}</Text>
    </Pressable>
  );
}

/** Photos first: live photos and video swipe across; the broker adds more (the owner approves them). */
function Gallery({ l, broker, onChange }: { l: Listing; broker: boolean; onChange: () => void }) {
  const { api } = useSession();
  const c = usePalette();
  const { width } = useWindowDimensions();
  const w = Math.min(width, 900);
  const [at, setAt] = useState(0);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState<unknown>(null);
  const media = l.owner_withdrew ? [] : (l.media ?? []);
  const photos = media.filter((m) => m.kind === 'photo');
  const video = media.find((m) => m.kind === 'video');
  const pending = broker ? (l.my_pending_media ?? []) : [];
  const upload = async (get: () => Promise<UploadFile[]>) => {
    setError(null);
    try {
      const files = await get();
      for (let i = 0; i < files.length; i++) {
        setBusy(`Uploading ${i + 1} of ${files.length}…`);
        await api.uploadListingMedia(l.id, files[i]);
      }
      if (files.length) onChange();
    } catch (e) {
      setError(e);
    } finally {
      setBusy('');
    }
  };
  return (
    <View style={{ backgroundColor: c.surface }}>
      <View style={{ height: 250, backgroundColor: c.surfaceAlt }}>
        {photos.length ? (
          <ScrollView horizontal pagingEnabled showsHorizontalScrollIndicator={false} onMomentumScrollEnd={(e) => setAt(Math.round(e.nativeEvent.contentOffset.x / w))} onScroll={(e) => Platform.OS === 'web' && setAt(Math.round(e.nativeEvent.contentOffset.x / w))} scrollEventThrottle={64}>
            {photos.map((m) => (
              <Pressable key={m.id} onPress={() => Linking.openURL(m.url)} accessibilityLabel="Open photo full size">
                <Image source={{ uri: m.url }} style={{ width: w, height: 250 }} resizeMode="cover" />
              </Pressable>
            ))}
          </ScrollView>
        ) : (
          <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', gap: 6 }}>
            <Text style={{ fontSize: 30, color: c.textMuted }}>▢</Text>
            <Text style={{ fontSize: 14, fontWeight: '700', color: c.textMuted }}>No photos yet</Text>
            {broker ? <Text style={{ fontSize: 12.5, color: c.textMuted }}>Add up to 5 photos and a walkthrough video below</Text> : null}
          </View>
        )}
        {photos.length ? <Pill style={{ left: 12, bottom: 12 }}>{`${Math.min(at + 1, photos.length)} / ${photos.length} photos`}</Pill> : null}
        {video ? (
          <Pressable onPress={() => Linking.openURL(video.url)} accessibilityRole="button" accessibilityLabel="Play walkthrough video" style={{ position: 'absolute', right: 12, bottom: 12 }}>
            <Pill>▶ Walkthrough</Pill>
          </Pressable>
        ) : null}
        {photos.length ? <Text style={{ position: 'absolute', left: 12, top: 12, backgroundColor: c.surface, color: c.ok, fontSize: 11, fontWeight: '700', paddingHorizontal: 9, paddingVertical: 4, borderRadius: 999, overflow: 'hidden' }}>Owner-approved</Text> : null}
      </View>
      {broker ? (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 6, padding: 8 }}>
          {[...photos, ...pending].map((m: MediaItem) => (
            <View key={m.id} style={{ width: 64, height: 48, borderRadius: 6, overflow: 'hidden', backgroundColor: c.surfaceAlt }}>
              {m.kind === 'photo' ? <Image source={{ uri: m.thumb_url }} style={{ width: 64, height: 48, opacity: m.state === 'pending' ? 0.45 : 1 }} /> : <Text style={{ textAlign: 'center', marginTop: 14 }}>▶</Text>}
              {m.state === 'pending' ? <Text style={{ position: 'absolute', bottom: 2, left: 2, right: 2, fontSize: 8.5, fontWeight: '700', color: c.warn, textAlign: 'center' }}>waiting</Text> : null}
            </View>
          ))}
          {busy ? <Text style={{ alignSelf: 'center', color: c.textMuted, fontSize: 12 }}>{busy}</Text> : (
            <>
              <MediaButton label="+ Photos" onPress={() => upload(() => pickFromGallery('photo', true))} testID="broker-add-photos" />
              {canUseCamera ? <MediaButton label="Camera" onPress={() => upload(takePhoto)} /> : null}
              <MediaButton label="+ Video" onPress={() => upload(() => pickFromGallery('video'))} />
            </>
          )}
        </ScrollView>
      ) : null}
      {broker && pending.length ? <P small muted>{`  ${pending.length} waiting for the owner’s approval before they go live.`}</P> : null}
      {error ? <View style={{ padding: 8 }}><ErrorBox error={error} /></View> : null}
    </View>
  );
}

function Pill({ children, style }: { children: React.ReactNode; style?: object }) {
  return <Text style={[{ position: 'absolute', backgroundColor: 'rgba(21,32,31,0.78)', color: '#FFFFFF', fontSize: 12, fontWeight: '700', paddingHorizontal: 10, paddingVertical: 5, borderRadius: 999, overflow: 'hidden' }, style]}>{children}</Text>;
}

function MediaButton({ label, onPress, testID }: { label: string; onPress: () => void; testID?: string }) {
  const c = usePalette();
  return (
    <Pressable onPress={onPress} accessibilityRole="button" style={{ height: 48, paddingHorizontal: 12, borderRadius: 6, backgroundColor: c.surfaceAlt, justifyContent: 'center' }} testID={testID}>
      <Text style={{ fontSize: 12, fontWeight: '700', color: c.brand }}>{label}</Text>
    </Pressable>
  );
}

/** Pick one of the broker's customers — those who fit come first — to share the flat with or plan a visit for. */
function CustomerPicker({ l, mode, onDone }: { l: Listing; mode: 'share' | 'visit'; onDone: () => void }) {
  const { api } = useSession();
  const c = usePalette();
  const [q, setQ] = useState('');
  const term = useDebounced(q.trim(), 300);
  const list = useQuery({ queryKey: ['customers', term], queryFn: () => api.customers(term || undefined) });
  const fits = l.page?.fitting_customers.customers ?? [];
  const share = useMutation({
    mutationFn: async (customerId: string) => {
      const sl = await api.createShortlist(customerId, [l.id]);
      await api.shareShortlist(sl.id);
    },
  });
  const pick = (customerId: string, name: string) => {
    if (mode === 'visit') {
      onDone();
      router.push(`/visit/new?customerId=${customerId}&customerName=${encodeURIComponent(name)}&listingId=${l.id}`);
    } else share.mutate(customerId);
  };
  const shown = [
    ...fits.map((f) => ({ id: f.customer_id, name: f.name, fit: true })),
    ...(list.data ?? []).filter((x) => !fits.some((f) => f.customer_id === x.id)).slice(0, 12).map((x) => ({ id: x.id, name: x.name || phone(x.phone), fit: false })),
  ];
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: 14, padding: 16, gap: 10, borderWidth: 2, borderColor: c.brand }}>
      <Row style={{ justifyContent: 'space-between' }}>
        <Text style={{ fontSize: 16, fontWeight: '800', color: c.text }}>{mode === 'share' ? 'Share with which customer?' : 'Plan a visit for which customer?'}</Text>
        <Pressable onPress={onDone} accessibilityRole="button" accessibilityLabel="Close"><Text style={{ color: c.textMuted, fontWeight: '700' }}>Close</Text></Pressable>
      </Row>
      {share.isSuccess ? (
        <Notice tone="ok">Sent. The customer gets a link with the photos, facts and area — never the flat number.</Notice>
      ) : (
        <>
          <TextInput value={q} onChangeText={setQ} placeholder="Search your customers" placeholderTextColor={c.textMuted} style={[{ borderWidth: 1, borderColor: c.border, borderRadius: 10, paddingHorizontal: 12, minHeight: 44, color: c.text, fontSize: 15 }, NO_OUTLINE]} accessibilityLabel="Search your customers" />
          {shown.map((x) => (
            <Pressable key={x.id} onPress={() => pick(x.id, x.name)} accessibilityRole="button" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', minHeight: 44, borderBottomWidth: 1, borderBottomColor: c.border }} testID={`pick-customer-${x.id}`}>
              <Text style={{ fontSize: 15, fontWeight: '600', color: c.text, flexShrink: 1 }}>{x.name}</Text>
              {x.fit ? <Chip label="Fits" tone="ok" /> : <Text style={{ color: c.brand, fontWeight: '700' }}>›</Text>}
            </Pressable>
          ))}
          {share.isPending ? <Loading /> : null}
          {share.error ? <ErrorBox error={share.error} /> : null}
        </>
      )}
    </View>
  );
}

function StatusPanel({ l, onDone }: { l: Listing; onDone: () => void }) {
  const { api } = useSession();
  const qc = useQueryClient();
  const c = usePalette();
  const rent = l.txn_type === 'RENT';
  const open = l.status === 'AVAILABLE' || l.status === 'AVAILABLE_UNCONFIRMED';
  const done = () => {
    qc.invalidateQueries({ queryKey: ['listings'] });
    onDone();
  };
  const status = useMutation({ mutationFn: (b: { state: string; on_behalf_of_owner?: boolean }) => api.reportStatus(l.id, b), onSuccess: done });
  const reconfirm = useMutation({ mutationFn: () => api.reconfirm(l.id), onSuccess: done });
  return (
    <View style={{ backgroundColor: c.surface, borderRadius: 14, padding: 16, gap: 10, borderWidth: 2, borderColor: c.brand }}>
      <Text style={{ fontSize: 16, fontWeight: '800', color: c.text }}>Status: {l.status_label}</Text>
      {l.status === 'AVAILABLE_UNCONFIRMED' ? <Notice tone="warn">Waiting for the owner’s YES. Owners confirm from a WhatsApp link — no app needed.</Notice> : null}
      <Row style={{ flexWrap: 'wrap' }}>
        {open ? (
          <>
            <Button small kind="secondary" title="Still available" onPress={() => reconfirm.mutate()} busy={reconfirm.isPending} />
            <Button small kind="secondary" title="Token / on hold" onPress={() => status.mutate({ state: 'ON_HOLD' })} />
            <Button small kind="danger" title={rent ? 'Rented out' : 'Sold'} onPress={() => confirm(`Mark this flat as ${rent ? 'rented out' : 'sold'}? Other brokers listing it will see the change (not who made it).`, () => status.mutate({ state: rent ? 'LET' : 'SOLD' }))} />
          </>
        ) : (
          <>
            <Button small title="Available again" onPress={() => status.mutate({ state: 'AVAILABLE' })} />
            <Button small kind="secondary" title="Owner confirmed on phone" onPress={() => confirm('Record that the owner told you on the phone that the flat is available?', () => status.mutate({ state: 'AVAILABLE', on_behalf_of_owner: true }))} />
          </>
        )}
      </Row>
      {status.error ? <ErrorBox error={status.error} /> : null}
    </View>
  );
}

function OwnerWithdrew({ id }: { id: string }) {
  const { api } = useSession();
  const c = usePalette();
  const [note, setNote] = useState('');
  const askBack = useMutation({ mutationFn: () => api.askOwnerBack(id, note) });
  return (
    <View style={{ margin: 12, backgroundColor: c.badBg, borderRadius: 14, padding: 16, gap: 8 }}>
      <Text style={{ fontSize: 15, fontWeight: '800', color: c.bad }}>The owner removed your firm from this flat</Text>
      <P small>It is hidden from matching, search and visit plans. You can’t add it again unless the owner allows you. If something went wrong, put it right and ask the owner — their decision is final.</P>
      {askBack.isSuccess ? <Notice tone="ok">Sent. The owner will decide.</Notice> : (
        <>
          <Field label="Message to the owner" value={note} onChangeText={setNote} placeholder="e.g. Sorry for the missed call — I’ve assigned a new staff member" multiline />
          <Button small title="Ask to be added back" disabled={!note.trim()} onPress={() => askBack.mutate()} busy={askBack.isPending} />
        </>
      )}
      {askBack.error ? <ErrorBox error={askBack.error} /> : null}
    </View>
  );
}
