from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from society.models import Society
from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from statutory.models import RegistrarSubmission
from society.models import Flat, SocietyMember
from society.models import MaintenanceBill, Payment
from society.models import FlatRecoveryStatus, NoticeLog

def build_structure_snapshot(society):

    flats = Flat.objects.filter(society=society)

    return {
        "total_flats": flats.count(),
        "active_flats": flats.filter(is_active=True).count(),
    }


def build_governance_snapshot(society):

    members = SocietyMember.objects.filter(society=society)

    return {
        "total_members": members.count(),
        "active_members": members.filter(is_active=True).count(),
    }


def build_finance_snapshot(society):

    bills = MaintenanceBill.objects.filter(society=society)
    payments = Payment.objects.filter(society=society)

    return {
        "bills_generated": bills.count(),
        "payments_received": payments.count(),
    }


def build_compliance_snapshot(society):

    recovery_cases = FlatRecoveryStatus.objects.filter(flat__society=society)
    notices = NoticeLog.objects.filter(society=society)

    return {
        "recovery_cases": recovery_cases.count(),
        "notices_issued": notices.count(),
    }

def preregistration_cockpit_view(request, society_id):
    """
    Chairman Cockpit — Thin aggregation layer.
    Extends snapshot with submission + lifecycle resolution.
    """

    society = get_object_or_404(Society, id=society_id)

    # 1) Core snapshot (source of truth)
    snapshot = preregistration_readiness_snapshot(society)

    registrar_ready = snapshot.get("registrar_ready", False)
    blockers = snapshot.get("blockers", [])

    # 2) Latest submission
    latest_submission = (
        RegistrarSubmission.objects
        .filter(society=society)
        .order_by("-submitted_at")
        .first()
    )

    if latest_submission:
        submission_data = {
            "status": latest_submission.status,
            "submitted_at": latest_submission.submitted_at,
        }
    else:
        submission_data = {
            "status": "NOT_SUBMITTED"
        }

    # --------------------------------------------------
    # 3) Lifecycle Stage Resolution (Priority Based)
    # --------------------------------------------------

    if getattr(society, "registration_number", None):
        stage = "REGISTERED"

    elif latest_submission:
        stage = "REGISTRATION_SUBMITTED"

    elif registrar_ready:
        stage = "READY_FOR_SUBMISSION"

    else:
        stage = "PRE_REGISTRATION"

    # --------------------------------------------------
    # 4) Determine next action
    # --------------------------------------------------

    if stage == "REGISTERED":
        next_action = None

    elif stage == "REGISTRATION_SUBMITTED":
        next_action = "Await Registrar approval"

    elif blockers:
        next_action = blockers[0].get("message")

    elif registrar_ready:
        next_action = "Submit to Registrar"

    else:
        next_action = "Complete pending obligations"

    # --------------------------------------------------
    # 5) Compose cockpit response
    # --------------------------------------------------
    
    structure_snapshot = build_structure_snapshot(society)
    governance_snapshot = build_governance_snapshot(society)
    finance_snapshot = build_finance_snapshot(society)
    compliance_snapshot = build_compliance_snapshot(society)

    return JsonResponse({
        "society": {
            "id": society.id,
            "name": society.name,
        },

        # lifecycle stage
        "stage": stage,
        "next_action": next_action,

        # prereg module
        "preregistration": {
            "snapshot": snapshot,
            "submission": submission_data,
        },

        # operations modules
        "structure": structure_snapshot,
        "governance": governance_snapshot,
        "finance": finance_snapshot,
        "compliance": compliance_snapshot,
    })

