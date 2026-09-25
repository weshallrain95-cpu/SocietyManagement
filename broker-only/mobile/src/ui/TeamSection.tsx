// The agency's team (founder decisions 2026-09-25): one Admin, managers, field staff — all on the same agency.
// The Admin adds managers and switches manager powers on or off; a manager the Admin allows can add field staff.
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import React, { useState } from 'react';
import { Alert, Linking, Platform, Text, View } from 'react-native';

import type { StaffMember, TeamPermission } from '@/api';
import { PERMISSION_LABEL, ROLE_LABEL, useAgency } from '@/auth/useAgency';
import { useSession } from '@/auth/session';
import { indianMobile } from '@/lib/format';
import { Button, Card, Chip, ChipRow, Choice, ErrorBox, Field, Notice, P, Row } from './components';
import { usePalette } from './theme';

const SWITCHES: TeamPermission[] = ['uploads', 'blasts', 'add_staff'];

function confirm(message: string, onYes: () => void) {
  if (Platform.OS === 'web') {
    if (window.confirm(message)) onYes();
  } else {
    Alert.alert('Please confirm', message, [{ text: 'No', style: 'cancel' }, { text: 'Yes', style: 'destructive', onPress: onYes }]);
  }
}

export function TeamSection() {
  const { api } = useSession();
  const qc = useQueryClient();
  const c = usePalette();
  const a = useAgency();
  const staff = useQuery({ queryKey: ['staff'], queryFn: api.staff });
  const [phone, setPhone] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<'broker_staff' | 'broker_manager'>('broker_staff');
  const [added, setAdded] = useState<{ phone: string; role: string } | null>(null);
  const refresh = () => qc.invalidateQueries({ queryKey: ['staff'] });
  const invite = useMutation({
    mutationFn: () => api.inviteStaff({ phone: indianMobile(phone)!, display_name: name, role }),
    onSuccess: () => {
      setAdded({ phone: indianMobile(phone)!, role });
      setPhone('');
      setName('');
      refresh();
    },
  });
  const perms = useMutation({
    mutationFn: ({ m, p }: { m: StaffMember; p: TeamPermission[] }) => api.setTeamPermissions(m.id, p),
    onSuccess: refresh,
  });
  const remove = useMutation({ mutationFn: (m: StaffMember) => api.removeStaff(m.id), onSuccess: refresh });
  const canAdd = a.isAdmin || a.can('add_staff');
  const agency = a.membership?.org_name ?? 'our agency';
  const members = (staff.data ?? []).filter((m) => m.active);
  const canRemove = (m: StaffMember) =>
    m.user_id !== a.me?.id && m.role !== 'broker_principal' && (a.isAdmin || (m.role === 'broker_staff' && a.can('add_staff')));

  return (
    <>
      {members.map((m) => (
        <Card key={m.id}>
          <Row style={{ justifyContent: 'space-between' }}>
            <P style={{ flexShrink: 1 }}>{m.name || 'Team member'}</P>
            <Chip label={ROLE_LABEL[m.role] ?? m.role} tone={m.role === 'broker_principal' ? 'info' : undefined} />
          </Row>
          {m.role === 'broker_manager' ? (
            a.isAdmin ? (
              <View style={{ gap: 4 }}>
                <Text style={{ fontSize: 12.5, color: c.textMuted }}>Allowed to (tap to switch on or off):</Text>
                <ChipRow>
                  {SWITCHES.map((p) => {
                    const on = !!m.permissions?.includes(p);
                    return (
                      <Chip
                        key={p}
                        label={`${on ? '✓ ' : ''}${PERMISSION_LABEL[p]}`}
                        selected={on}
                        onPress={() => perms.mutate({ m, p: on ? (m.permissions ?? []).filter((x) => x !== p) : [...(m.permissions ?? []), p] })}
                      />
                    );
                  })}
                </ChipRow>
              </View>
            ) : m.permissions?.length ? (
              <P small muted>Also allowed: {m.permissions.map((p) => PERMISSION_LABEL[p]).join(', ')}</P>
            ) : null
          ) : null}
          {canRemove(m) ? (
            <Button
              small
              kind="ghost"
              title="Remove from team"
              onPress={() => confirm(`Remove ${m.name || 'this person'} from the team? They lose access at once; any keys they hold are flagged for handover.`, () => remove.mutate(m))}
            />
          ) : null}
        </Card>
      ))}
      {perms.error ? <ErrorBox error={perms.error} /> : null}
      {remove.error ? <ErrorBox error={remove.error} /> : null}

      {canAdd ? (
        <Card>
          <P style={{ fontWeight: '600' }}>Add a team member</P>
          <Field label="Mobile number" keyboardType="phone-pad" value={phone} onChangeText={setPhone} />
          <Field label="Name" value={name} onChangeText={setName} />
          {a.isAdmin ? (
            <Choice value={role} onChange={setRole} options={[{ value: 'broker_staff', label: 'Field staff' }, { value: 'broker_manager', label: 'Manager' }]} />
          ) : null}
          <Button title="Add" onPress={() => invite.mutate()} disabled={!indianMobile(phone)} busy={invite.isPending} />
          {invite.error ? <ErrorBox error={invite.error} /> : null}
          {added ? (
            <Notice tone="ok">
              Added. Let them know: they install Only Broker, choose “I’m a broker” and sign in with this number.
            </Notice>
          ) : null}
          {added ? (
            <Button
              small
              kind="secondary"
              title="Send them a WhatsApp message"
              onPress={() =>
                Linking.openURL(
                  `https://wa.me/91${added.phone.replace(/\D/g, '').slice(-10)}?text=${encodeURIComponent(
                    `You've been added to ${agency} on Only Broker as ${ROLE_LABEL[added.role]}. Install the Only Broker app, choose "I'm a broker" and sign in with this number.`,
                  )}`,
                )
              }
            />
          ) : null}
          <Notice>
            Managers run the day: flats, customers, trips. Uploads, blasts and adding field staff only if you switch them on. Field staff see only the visits
            given to them, with owner numbers hidden, and can add walk-in customers.
          </Notice>
        </Card>
      ) : (
        <P small muted>Only your agency Admin can add team members.</P>
      )}
    </>
  );
}
