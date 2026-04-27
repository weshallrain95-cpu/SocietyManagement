from django.db.models import Count

from society.models import Flat, FlatOwnership, ShareCertificate, Committee
from statutory.models import SocietyBylaws


def _has_structure(society_id):
    return Flat.objects.filter(society_id=society_id).exists()


def _ownership_summary(society_id):
    flats = Flat.objects.filter(society_id=society_id).count()

    active_ownerships = FlatOwnership.objects.filter(
        flat__society_id=society_id,
        is_active=True
    ).values("flat").distinct().count()

    return {
        "total_flats": flats,
        "owned_flats": active_ownerships,
        "is_complete": flats > 0 and flats == active_ownerships
    }


def _has_committee(society_id):
    return Committee.objects.filter(
        society_id=society_id,
        is_active=True
    ).exists()


def _has_bylaws_signed(society_id):
    return SocietyBylaws.objects.filter(
        society_id=society_id,
        status="SIGNED"
    ).exists()


def _share_certificate_summary(society_id):
    qs = ShareCertificate.objects.filter(society_id=society_id)

    total = qs.count()
    issued = qs.filter(status="ISSUED").count()

    return {
        "total": total,
        "issued": issued,
        "is_generated": total > 0,
        "is_fully_issued": total > 0 and total == issued
    }

def _has_operational_rules(society_id):
    from society.models import OperationalRule, BillingRule

    try:
        billing = BillingRule.objects.get(society_id=society_id)
        operational = OperationalRule.objects.get(
            society_id=society_id,
            is_active=True
        )
    except (BillingRule.DoesNotExist, OperationalRule.DoesNotExist):
        return False

    # 🔹 SCR17 — BillingRule must be configured
    billing_configured = (
        billing.billing_start_date is not None and
        isinstance(billing.charges, list) and
        len(billing.charges) > 0
    )

    # 🔹 SCR18 — governance interaction
    operational_configured = (
        operational.dispute_enabled or
        operational.dispute_hold_bill or
        not operational.dispute_apply_interest or
        operational.vacant_type != "FULL" or
        operational.vacant_value is not None or
        operational.manager_enabled
    )

    # 🔹 SCR19 — financial controls must be fully configured
    financial_controls_complete = (
        operational.max_spend_without_approval is not None and
        operational.committee_approval_limit is not None and
        getattr(operational, "max_cash_spend_allowed", None) is not None and
        getattr(operational, "financial_controls_configured", False)
    )

    return (
        billing_configured and
        operational_configured and
        financial_controls_complete
    )                                 

def _has_registration_compliance(society_id):
    from society.models import Society

    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return False

    is_registered = bool(getattr(society, "registration_number", None))

    if not is_registered:
        return True

    return (
        getattr(society, "registration_certificate", None) is not None and
        getattr(society, "oc_certificate", None) is not None
    )

def derive_onboarding_state(society_id):

    if not _has_structure(society_id):
        return "STRUCTURE_PENDING"

    ownership = _ownership_summary(society_id)

    if not ownership["owned_flats"]:
        return "OWNERSHIP_PENDING"

    if not ownership["is_complete"]:
        return "OWNERSHIP_REFINEMENT_PENDING"

    if not _has_committee(society_id):
        return "OPERATIONS_PENDING"

    if not _has_bylaws_signed(society_id):
        return "BYLAWS_PENDING"

    share = _share_certificate_summary(society_id)

    if not share["is_generated"]:
        return "SHARE_CERTIFICATES_PENDING"

    if not share["is_fully_issued"]:
        return "SHARE_CERTIFICATES_PENDING"


    # 🔥 NEW: Operational Rules Check
    if not _has_operational_rules(society_id):
        return "OPERATIONAL_RULES_PENDING"

    # 🔥 Registration compliance gate
    if not _has_registration_compliance(society_id):
        return "OPERATIONAL_RULES_PENDING"

    return "OPERATIONS_COMPLETE"


def derive_allowed_actions(society_id):

    ownership = _ownership_summary(society_id)
    has_committee = _has_committee(society_id)
    has_bylaws = _has_bylaws_signed(society_id)
    share = _share_certificate_summary(society_id)
    has_operational_rules = _has_operational_rules(society_id)

    return {
        "can_upload_ownership": ownership["total_flats"] > 0 and ownership["owned_flats"] == 0,

        "needs_refinement": (
            ownership["owned_flats"] > 0 and not ownership["is_complete"]
        ),

        "can_create_committee": ownership["is_complete"] and not has_committee,

        "can_generate_bylaws": has_committee and not has_bylaws,

        "can_access_share_certificates": (
            has_bylaws and (
                not share["is_generated"] or not share["is_fully_issued"]
            )
        ),

        "can_generate_share_certificates": has_bylaws and not share["is_generated"],

        "can_issue_share_certificates": (
            share["is_generated"] and not share["is_fully_issued"]
        ),

        "can_configure_operational_rules": (
            share["is_fully_issued"] and not has_operational_rules
        ),
        
        "is_complete": derive_onboarding_state(society_id) == "OPERATIONS_COMPLETE",
    }