// The agency's business details: the Admin edits them; everyone else in the agency can read them.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React from 'react';

import { useAgency } from '@/auth/useAgency';
import { useSession } from '@/auth/session';
import { AgencyFormView } from '@/ui/AgencyFormView';
import { Card, Chip, ErrorBox, Loading, Notice, P, Row, Screen } from '@/ui/components';

const STATUS = { pending: ['Waiting for verification', 'warn'], verified: ['Verified', 'ok'], rejected: ['Not verified', 'bad'], suspended: ['Suspended', 'bad'] } as const;

export default function AgencyDetails() {
  const { api } = useSession();
  const qc = useQueryClient();
  const a = useAgency();
  const q = useQuery({ queryKey: ['agency'], queryFn: api.myAgency });
  const save = useMutation({ mutationFn: api.updateAgency, onSuccess: (org) => qc.setQueryData(['agency'], org) });
  if (q.isLoading) return <Screen><Loading /></Screen>;
  if (q.error || !q.data) return <Screen><ErrorBox error={q.error} onRetry={q.refetch} /></Screen>;
  const org = q.data;
  const [label, tone] = STATUS[org.verification_status];
  return (
    <Screen>
      <Card>
        <Row style={{ justifyContent: 'space-between' }}>
          <P style={{ fontWeight: '700', flexShrink: 1 }}>{org.name}</P>
          <Chip label={label} tone={tone} />
        </Row>
        {org.verification_note ? <P small muted>{org.verification_note}</P> : null}
      </Card>
      {save.isSuccess ? <Notice tone="ok">Saved.</Notice> : null}
      {a.isAdmin ? (
        <AgencyFormView key={org.id} mode="edit" initial={org} busy={save.isPending} error={save.error} onSubmit={(f) => save.mutate(f)} />
      ) : (
        <>
          <Card>
            <P>{org.legal_name}</P>
            <P small muted>{org.owners.map((o) => `${o.role}: ${o.name}`).join(' · ')}</P>
            <P small muted>{[org.office_address, org.office_address_2, org.office_city, org.office_pincode].filter(Boolean).join(', ')}</P>
            <P small muted>MahaRERA {org.rera_agent_no || '—'} · GST {org.gst_registered ? org.gstin : 'not registered'}</P>
          </Card>
          <P small muted>Only the agency Admin can change these details.</P>
        </>
      )}
    </Screen>
  );
}
