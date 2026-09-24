import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import React from 'react';
import { Linking } from 'react-native';

import type { VisitPlan } from '@/api';
import { useSession } from '@/auth/session';
import { dayLabel, time } from '@/lib/format';
import { Button, Card, Chip, ErrorBox, H1, H2, Loading, Notice, P, Row, Screen } from '@/ui/components';
import { FlatSearch } from '@/ui/FlatSearch';

const ISSUE: Record<string, string> = {
  no_key_recorded: 'No key location recorded',
  key_with_owner: 'Key is with the owner — coordinate before leaving',
  key_with_society_office: 'Key is at the society office',
  key_needs_handover: 'Key holder left the team — arrange handover',
  same_flat_booked_in_another_plan_at_overlapping_time: 'Same flat booked in another plan at the same time',
};

export default function VisitPlanScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { api } = useSession();
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['plan', id], queryFn: () => api.visitPlan(id) });
  const staff = useQuery({ queryKey: ['staff'], queryFn: api.staff });
  const act = useMutation({
    mutationFn: ({ action, body }: { action: string; body?: Record<string, unknown> }) => api.planAction(id, action, body),
    onSuccess: (r) => {
      if ((r as VisitPlan).stops) qc.setQueryData(['plan', id], r);
      else q.refetch();
      qc.invalidateQueries({ queryKey: ['plans'] });
    },
  });
  const remove = useMutation({ mutationFn: (stopId: string) => api.removeStop(id, stopId), onSuccess: (p) => qc.setQueryData(['plan', id], p) });

  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (!q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const p = q.data;
  const fieldStaff = staff.data?.filter((m) => m.role === 'broker_staff') ?? [];
  const move = (i: number, dir: -1 | 1) => {
    const ids = p.stops.map((s) => s.id);
    const j = i + dir;
    if (j < 0 || j >= ids.length) return;
    [ids[i], ids[j]] = [ids[j], ids[i]];
    act.mutate({ action: 'reorder', body: { stop_ids: ids } });
  };

  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      <H1>{p.customer_name || 'Visit plan'}</H1>
      <P muted>{dayLabel(p.date)} · starts {p.start_time.slice(0, 5)} · {p.total_travel_min ?? '?'} min travel · v{p.version}</P>
      <Row style={{ flexWrap: 'wrap' }}>
        <Chip label={p.state.replace(/_/g, ' ')} tone={p.state === 'customer_confirmed' ? 'ok' : 'info'} />
      </Row>
      {p.key_warnings?.map((w, i) => <Notice key={i} tone="warn">🔑 {ISSUE[w.issue] ?? w.issue}</Notice>)}

      <H2>Route</H2>
      {p.stops.map((s, i) => (
        <Card key={s.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{s.seq}. {s.society}</P>
            <P>{time(s.slot_start)}</P>
          </Row>
          <P muted small>{s.building} · Flat {s.unit_no} · owner notice: {s.owner_notice.replace(/_/g, ' ')}{s.outcome ? ` · ${s.outcome.replace(/_/g, ' ')}` : ''}</P>
          <Row style={{ flexWrap: 'wrap' }}>
            <Button small kind="secondary" title="Navigate" onPress={() => Linking.openURL(s.navigate_url)} />
            <Button small kind="ghost" title="↑" onPress={() => move(i, -1)} disabled={i === 0} />
            <Button small kind="ghost" title="↓" onPress={() => move(i, 1)} disabled={i === p.stops.length - 1} />
            <Button small kind="ghost" title="Remove" onPress={() => remove.mutate(s.id)} />
          </Row>
        </Card>
      ))}

      <H2>Add a flat</H2>
      <FlatSearch
        label="Society and flat number you have in mind"
        pickedIds={p.stops.map((s) => s.listing_id)}
        onPick={(l) => act.mutate({ action: 'add-stop', body: { listing_id: l.id } })}
        addParams={{ plan: p.id }}
      />

      <H2>Send & assign</H2>
      <Button title="Share plan with customer" onPress={() => act.mutate({ action: 'share' })} busy={act.isPending && act.variables?.action === 'share'} />
      <Button kind="secondary" title="Notify owners" onPress={() => act.mutate({ action: 'notify-owners' })} />
      <Button kind="secondary" title="Re-optimise route" onPress={() => act.mutate({ action: 'optimise' })} />
      {fieldStaff.length ? (
        <>
          <P small style={{ fontWeight: '600' }}>Assign to</P>
          <Row style={{ flexWrap: 'wrap' }}>
            {fieldStaff.map((m) => (
              <Button key={m.user_id} small kind="secondary" title={m.name || 'Staff'} onPress={() => act.mutate({ action: 'assign', body: { staff_user_id: m.user_id } })} />
            ))}
          </Row>
        </>
      ) : <Notice>Add field staff under More → Team to assign visits.</Notice>}
      {act.error || remove.error ? <ErrorBox error={act.error ?? remove.error} /> : null}
      <Notice>Changes reach assigned staff and the customer’s link instantly. Customers see exact flat numbers only after they confirm.</Notice>
      <Button kind="danger" title="Cancel plan" onPress={() => act.mutate({ action: 'cancel' })} />
    </Screen>
  );
}
