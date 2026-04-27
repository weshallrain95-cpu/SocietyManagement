from society.models import (
    OperationalRule,
    SocietyOfficeBearer,
    SocietyMember,
    SocietyManager,
    CommitteeMembership,
)


def get_user_role(user, society):
    """
    Resolve user's role in the society
    """

    # 1. Society Manager
    try:
        manager = SocietyManager.objects.get(society=society, is_active=True)
        if manager.user == user:
            return "MANAGER"
    except SocietyManager.DoesNotExist:
        pass

    # 2. Society Member
    try:
        member = SocietyMember.objects.get(user=user, society=society)
    except SocietyMember.DoesNotExist:
        return "MEMBER"

    # 3. Office Bearer (Chairman / Treasurer etc.)
    try:
        office_bearer = SocietyOfficeBearer.objects.get(
            society=society,
            committee_membership_ref__member=member,
            is_active=True
        )
        return office_bearer.role
    except SocietyOfficeBearer.DoesNotExist:
        pass

    # 4. Committee Member (no office)
    is_committee = CommitteeMembership.objects.filter(
        society=society,
        member=member,
        is_active=True
    ).exists()

    if is_committee:
        return "COMMITTEE_MEMBER"

    # 5. Default
    return "MEMBER"


def can_user_create(user, society):
    """
    Determines if user can initiate an action (maker)
    """

    try:
        OperationalRule.objects.get(society=society)
    except OperationalRule.DoesNotExist:
        return False

    role = get_user_role(user, society)

    # ✅ Manager — always maker
    if role == "MANAGER":
        return True

    # ✅ Chairman / Treasurer — maker allowed
    if role in ["CHAIRMAN", "TREASURER"]:
        return True

    # ✅ Committee members — maker
    if role == "COMMITTEE_MEMBER":
        return True

    # ❌ Regular members — cannot create
    return False

def can_user_approve(user, society, current_approvals=None):
    """
    Determines if user can approve an action

    current_approvals = list of roles who have already approved
    (e.g. ["CHAIRMAN"])
    """

    if current_approvals is None:
        current_approvals = []

    try:
        rule = OperationalRule.objects.get(society=society)
    except OperationalRule.DoesNotExist:
        return False

    role = get_user_role(user, society)

    # ❌ Manager can NEVER approve
    if role == "MANAGER":
        return False

    # ❌ Only Chairman / Treasurer are checkers
    if role not in ["CHAIRMAN", "TREASURER"]:
        return False

    # 🔹 SINGLE APPROVAL MODE
    if rule.approval_mode == "SINGLE":
        return True

    # 🔹 DUAL APPROVAL MODE
    if rule.approval_mode == "DUAL":

        # Already approved by this role
        if role in current_approvals:
            return False

        # If no approvals yet → allow
        if len(current_approvals) == 0:
            return True

        # If one approval exists → allow only if different role
        if len(current_approvals) == 1:
            return role != current_approvals[0]

        # Already fully approved
        return False

    return False