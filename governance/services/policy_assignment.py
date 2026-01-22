# governance/services/policy_assignment.py

from governance.models import Policy, PolicyAssignment


class PolicyAssignmentService:

    @staticmethod
    def assign_policy(
        *,
        policy_code: str,
        role: str = None,
        user_id: str = None,
        society_id: str = None
    ):
        policy = Policy.objects.filter(code=policy_code, is_active=True).first()

        if not policy:
            raise ValueError(f"Active policy not found: {policy_code}")

        assignment, created = PolicyAssignment.objects.get_or_create(
            policy=policy,
            role=role,
            user_id=user_id,
            society_id=society_id
        )

        return assignment

    @staticmethod
    def get_applicable_policies(
        *,
        user_id=None,
        role=None,
        society_id=None
    ):
        """
        Returns policies in resolution priority order
        USER → ROLE → SOCIETY → SYSTEM
        """

        qs = PolicyAssignment.objects.select_related("policy").filter(
            policy__is_active=True
        )

        ordered = []

        # USER
        if user_id:
            ordered += list(qs.filter(user_id=user_id))

        # ROLE
        if role:
            ordered += list(qs.filter(role=role, user_id__isnull=True))

        # SOCIETY
        if society_id:
            ordered += list(qs.filter(society_id=society_id, user_id__isnull=True, role__isnull=True))

        # SYSTEM DEFAULTS
        ordered += list(qs.filter(
            user_id__isnull=True,
            role__isnull=True,
            society_id__isnull=True
        ))

        # Deduplicate by policy id while preserving order
        seen = set()
        unique = []
        for a in ordered:
            if a.policy_id not in seen:
                seen.add(a.policy_id)
                unique.append(a.policy)

        return unique
