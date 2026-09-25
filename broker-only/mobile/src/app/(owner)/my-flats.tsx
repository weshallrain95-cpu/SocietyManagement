import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import React from 'react';

import { useSession } from '@/auth/session';
import { bhk } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, Loading, P, Row, Screen } from '@/ui/components';

export default function MyFlats() {
  const { api } = useSession();
  const q = useQuery({ queryKey: ['owner-flats'], queryFn: api.ownerFlats });
  const me = useQuery({ queryKey: ['me'], queryFn: api.me });
  const first = me.data?.display_name?.trim().split(/\s+/)[0];
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      {first ? <P style={{ fontWeight: '700', fontSize: 18 }}>Namaste {first} — your flats, your rules.</P> : null}
      <Button title="+ Add my flat" onPress={() => router.push('/owner/new')} testID="add-my-flat" />
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {q.data?.length === 0 ? <Empty title="No flats yet" body="Add your flat, then add photos and choose which brokers may handle it." /> : null}
      {q.data?.map((f) => {
        const allowed = f.brokers.filter((b) => b.allowed);
        return (
          <Card key={f.id} onPress={() => router.push(`/owner/${f.id}`)} testID={`flat-${f.unit_no}`}>
            <P style={{ fontWeight: '700' }}>{f.society}</P>
            <P muted small>{f.building} · Flat {f.unit_no} · {bhk(f.bhk)}</P>
            <Row style={{ flexWrap: 'wrap' }}>
              {f.statuses.length ? f.statuses.map((s) => <Chip key={s.txn_type} label={s.label} tone={s.state === 'AVAILABLE' ? 'ok' : 'info'} />) : <Chip label="Not listed by any broker yet" />}
            </Row>
            <P small muted>
              {allowed.length ? `Handled by ${allowed.map((b) => b.name).join(', ')}` : 'No broker is handling it yet'} · {f.photo_count} photos · {f.video_count} videos
            </P>
          </Card>
        );
      })}
    </Screen>
  );
}
