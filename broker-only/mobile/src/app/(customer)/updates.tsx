// A customer's updates from the brokers they deal with. They can turn any broker's updates off.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useEffect } from 'react';

import { useSession } from '@/auth/session';
import { ago } from '@/lib/format';
import { Button, Card, Chip, Empty, ErrorBox, Loading, P, Row, Screen } from '@/ui/components';

export default function Updates() {
  const { api } = useSession();
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ['my-updates'], queryFn: api.myUpdates });
  const unread = q.data?.some((u) => !u.read);
  useEffect(() => {
    if (unread) api.markUpdatesRead().catch(() => undefined);
  }, [unread, api]);
  const mute = useMutation({
    mutationFn: ({ orgId, muted }: { orgId: string; muted: boolean }) => api.muteBroker(orgId, muted),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['my-updates'] }),
  });
  return (
    <Screen onRefresh={q.refetch} refreshing={q.isFetching}>
      {q.isLoading ? <Loading /> : q.error ? <ErrorBox error={q.error} onRetry={q.refetch} /> : null}
      {q.data?.length === 0 ? <Empty title="No updates yet" body="Your brokers’ news about new flats and prices will appear here." /> : null}
      {q.data?.map((u) => (
        <Card key={u.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ fontWeight: '700', flexShrink: 1 }}>{u.org}</P>
            <P small muted>{ago(u.sent_at)}</P>
          </Row>
          {u.flat ? (
            <Row style={{ flexWrap: 'wrap' }}>
              <Chip label={`${u.flat.bhk} · ${u.flat.society}`} tone="info" />
              {u.flat.price_label ? <Chip label={u.flat.price_label} /> : null}
            </Row>
          ) : null}
          <P>{u.text}</P>
          <Button
            small
            kind="ghost"
            title={u.muted ? `Turn ${u.org}’s updates back on` : `Stop updates from ${u.org}`}
            onPress={() => mute.mutate({ orgId: u.org_id, muted: !u.muted })}
          />
        </Card>
      ))}
      {mute.error ? <ErrorBox error={mute.error} /> : null}
    </Screen>
  );
}
