from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from society.models import (
    Society,
    Flat,
    SocietyMember,
    MaintenanceBill,
    Payment,
    FlatRecoveryStatus,
    NoticeLog,
    Case
)

from statutory.models import RegistrarSubmission
from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from statutory.health_engine import calculate_society_health_score


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


def build_member_snapshot(society):

    members = SocietyMember.objects.filter(society=society)

    return {
        "total_members": members.count(),
        "active_members": members.filter(is_active=True).count(),
    }


def build_legal_snapshot(society):

    cases = Case.objects.filter(society=society)

    return {
        "active_cases": cases.count()
    }


def build_intelligence_snapshot(society):

    score = calculate_society_health_score(society)

    return {
        "health_score": score
    }


def build_lifecycle_snapshot(society, registrar_ready, latest_submission):

    if getattr(society, "registration_number", None):
        stage = "REGISTERED"

    elif latest_submission:
        stage = "REGISTRATION_SUBMITTED"

    elif registrar_ready:
        stage = "READY_FOR_SUBMISSION"

    else:
        stage = "PRE_REGISTRATION"

    return {"stage": stage}


def preregistration_cockpit_view(request, society_id):

    society = get_object_or_404(Society, id=society_id)

    snapshot = preregistration_readiness_snapshot(society)

    registrar_ready = snapshot.get("registrar_ready", False)
    blockers = snapshot.get("blockers", [])

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
        submission_data = {"status": "NOT_SUBMITTED"}

    lifecycle = build_lifecycle_snapshot(
        society,
        registrar_ready,
        latest_submission
    )

    stage = lifecycle["stage"]

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

    structure_snapshot = build_structure_snapshot(society)
    governance_snapshot = build_governance_snapshot(society)
    finance_snapshot = build_finance_snapshot(society)
    compliance_snapshot = build_compliance_snapshot(society)
    members_snapshot = build_member_snapshot(society)
    legal_snapshot = build_legal_snapshot(society)
    intelligence_snapshot = build_intelligence_snapshot(society)

    return JsonResponse({

        "society": {
            "id": society.id,
            "name": society.name,
        },

        "lifecycle": lifecycle,

        "structure": structure_snapshot,
        "members": members_snapshot,
        "governance": governance_snapshot,
        "finance": finance_snapshot,
        "compliance": compliance_snapshot,
        "legal": legal_snapshot,

        "intelligence": intelligence_snapshot,

        "next_action": next_action,

        "preregistration": {
            "snapshot": snapshot,
            "submission": submission_data,
        },
    })
