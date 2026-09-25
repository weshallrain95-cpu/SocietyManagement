import { router } from 'expo-router';
import React, { useState } from 'react';
import { Linking } from 'react-native';

import { useSession } from '@/auth/session';
import { dayLabel, OUTCOMES, time } from '@/lib/format';
import { useOfflineDay } from '@/lib/useOfflineDay';
import { Button, Card, Chip, ChipRow, Empty, H2, Notice, P, Row, Screen } from '@/ui/components';

export default function MyDay() {
  const { tokens } = useSession();
  const { plans, pending, online, syncing, error, lastSync, sync, record } = useOfflineDay();
  const [open, setOpen] = useState<string | null>(null);
  const myStops = plans.flatMap((p) => p.stops.filter((s) => !s.assigned_staff_id || tokens?.role === 'broker_staff').map((s) => ({ plan: p, stop: s })));

  return (
    <Screen onRefresh={sync} refreshing={syncing}>
      <Row style={{ flexWrap: 'wrap' }}>
        <Chip label={online ? 'Online' : 'Offline – working from saved plan'} tone={online ? 'ok' : 'warn'} />
        {pending.length ? <Chip label={`${pending.length} waiting to sync`} tone="warn" /> : <Chip label="All synced" tone="ok" />}
      </Row>
      {error && !online ? null : error ? <Notice tone="warn">{error}</Notice> : null}
      {lastSync ? <P small muted>Last synced {time(lastSync)}</P> : null}
      <Button kind="secondary" title="+ Walk-in customer" onPress={() => router.push('/walk-in')} testID="walk-in" />

      {myStops.length === 0 ? <Empty title="No visits assigned" body="Your broker will assign visits here. Pull down to refresh." /> : null}
      {plans.map((p) => (
        <React.Fragment key={p.id}>
          <H2>{dayLabel(p.date)} · {p.start_time.slice(0, 5)} · {p.customer_name || 'Customer'}</H2>
          {p.stops.map((s) => (
            <Card key={s.id} onPress={() => setOpen(open === s.id ? null : s.id)}>
              <Row style={{ justifyContent: 'space-between' }}>
                <P style={{ fontWeight: '700', flexShrink: 1 }}>{s.seq}. {s.society}</P>
                <P>{time(s.slot_start)}</P>
              </Row>
              <P muted small>{s.building} · Flat {s.unit_no}</P>
              <Row style={{ flexWrap: 'wrap' }}>
                {s.checkin_at ? <Chip label={`Checked in ${time(s.checkin_at)}`} tone="ok" /> : null}
                {s.outcome ? <Chip label={s.outcome.replace(/_/g, ' ')} tone="info" /> : null}
              </Row>
              {open === s.id ? (
                <>
                  <Row style={{ flexWrap: 'wrap' }}>
                    <Button small kind="secondary" title="Navigate" onPress={() => Linking.openURL(s.navigate_url)} />
                    {!s.checkin_at ? <Button small title="Check in" onPress={() => record({ entity: 'checkin', stop_id: s.id })} testID={`checkin-${s.seq}`} /> : null}
                  </Row>
                  <P small style={{ fontWeight: '600' }}>Outcome</P>
                  <ChipRow>
                    {OUTCOMES.map((o) => (
                      <Button key={o.value} small kind={s.outcome === o.value ? 'primary' : 'secondary'} title={o.label} onPress={() => record({ entity: 'outcome', stop_id: s.id, outcome: o.value })} />
                    ))}
                  </ChipRow>
                </>
              ) : null}
            </Card>
          ))}
        </React.Fragment>
      ))}
      <Notice>Works without network: check-ins and outcomes are saved on the phone and sent automatically when you are back online. Nothing is sent twice.</Notice>
      <Button kind="secondary" title={syncing ? 'Syncing…' : 'Sync now'} onPress={sync} disabled={syncing} />
    </Screen>
  );
}
