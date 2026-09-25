// Who the signed-in person is inside their agency, and what they may do beyond day-to-day work.
import { useQuery } from '@tanstack/react-query';

import type { TeamPermission } from '@/api';
import { useSession } from './session';

export const ROLE_LABEL: Record<string, string> = {
  broker_principal: 'Admin',
  broker_manager: 'Manager',
  broker_staff: 'Field staff',
};

export const PERMISSION_LABEL: Record<TeamPermission, string> = {
  uploads: 'Excel uploads',
  blasts: 'Blasts (co-broking and customer updates)',
  add_staff: 'Add and remove field staff',
};

export function useAgency() {
  const { api, tokens } = useSession();
  const me = useQuery({ queryKey: ['me'], queryFn: api.me, enabled: !!tokens });
  const m = me.data?.memberships.find((x) => x.org_id === me.data?.active_org_id);
  const role = m?.role ?? tokens?.role ?? null;
  const isAdmin = role === 'broker_principal';
  return {
    loading: me.isLoading,
    me: me.data,
    membership: m,
    role,
    isAdmin,
    can: (p: TeamPermission) => isAdmin || !!m?.can?.includes(p),
  };
}
