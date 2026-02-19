from django.shortcuts import render

def status_selection(request):
    return render(request, "core/status_selection.html")

from django.shortcuts import render, redirect

def case_initiation(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        designation = request.POST.get("designation")

        # temporary — just proceed forward
        return redirect("/bylaws/")

    return render(request, "core/case_initiation.html")


from society.models import Person, Case
from django.shortcuts import render, redirect


def case_initiation(request):
    return render(request, "core/case_initiation.html")


from django.shortcuts import render, redirect
from django.db import transaction
import traceback

from society.models import Person, Case, CaseStage


def case_create(request):
    """
    Creates a new pre-registration case.

    Flow:
    1. Get / create Person (phone = unique identity)
    2. Prevent duplicate active prereg case
    3. Create new Case
    4. Auto-create BylawDraft
    5. Auto-create CaseStage spine
    6. Redirect to Case Dashboard
    """

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")

        try:
            with transaction.atomic():

                # STEP 1 — Person identity
                person, _ = Person.objects.get_or_create(
                    phone=phone,
                    defaults={"full_name": name or "Unknown"}
                )

                # STEP 2 — prevent duplicate active prereg case
                existing_case = Case.objects.filter(
                    initiated_by=person,
                    case_type="prereg",
                    status="initiated"
                ).first()

                if existing_case:
                    return redirect(f"/case/{existing_case.id}/")

                # STEP 3 — create new case
                new_case = Case.objects.create(
                    initiated_by=person,
                    case_type="prereg",
                    status="initiated"
                )

                # STEP 4 — auto-create bylaws draft
                from statutory.bylaws.models import BylawDraft

                BylawDraft.objects.get_or_create(
                    case=new_case,
                    defaults={"version_code": "MH-2014"}
                )

                # STEP 5 — create case stage spine
                STAGES = [
                    "member_list",
                    "share_structure",
                    "entrance_fees",
                    "promoter_affidavit",
                    "bank_account",
                    "building_docs",
                    "oc_cc",
                    "land_docs",
                    "builder_noc",
                    "society_resolution",
                    "bylaws_final",
                ]

                CaseStage.objects.bulk_create([
                    CaseStage(
                        case=new_case,
                        stage_code=stage,
                        status="pending"
                    )
                    for stage in STAGES
                ])

            # STEP 6 — redirect to dashboard
            return redirect(f"/case/{new_case.id}/")

        except Exception as exc:
            print("CASE_CREATE_ERROR:")
            print(traceback.format_exc())
            return render(request, "core/error.html", {"error": str(exc)})

    # GET request
    return render(request, "core/case_form.html")


from society.models import Case, CaseStage
from django.shortcuts import render, get_object_or_404

def case_dashboard(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    stages = CaseStage.objects.filter(case=case).order_by("id")

    context = {
        "case": case,
        "stages": stages
    }

    return render(request, "core/case_dashboard.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from society.models import Case, CaseStage


def stage_router(request, case_id, stage_code):
    case = get_object_or_404(Case, id=case_id)
    stage = get_object_or_404(
        CaseStage,
        case=case,
        stage_code=stage_code
    )

    # STEP 1 — checklist acknowledgement
    if request.method == "POST":
        acknowledged = request.POST.get("acknowledged")

        if acknowledged:
            return redirect(f"/case/{case.id}/stage/{stage_code}/decisions/")

    context = {
        "case": case,
        "stage": stage,
    }

    return render(request, "core/stage_checklist.html", context)

from django.shortcuts import get_object_or_404, redirect, render
from society.models import Case, CaseStage


def stage_entry(request, case_id, stage_code):
    """
    Entry router for a stage.

    Flow:
    Dashboard → Checklist → Decisions → Form
    """

    case = get_object_or_404(Case, id=case_id)
    stage = get_object_or_404(CaseStage, case=case, stage_code=stage_code)

    # STEP 1 — open checklist page first
    return redirect(f"/case/{case.id}/stage/{stage.stage_code}/checklist/")

def stage_checklist(request, case_id, stage_code):
    case = get_object_or_404(Case, id=case_id)
    stage = get_object_or_404(CaseStage, case=case, stage_code=stage_code)

    if request.method == "POST":
        return redirect(f"/case/{case.id}/stage/{stage.stage_code}/decisions/")

    return render(
        request,
        "core/stage_checklist.html",
        {
            "case": case,
            "stage": stage,
        }
    )

from bylaws.models import (
    BylawDecision,
    BylawDraft,
    DecisionSession
)
from django.shortcuts import render, get_object_or_404, redirect


def decision_workspace(request, case_id, stage_code):
    """
    Decision workspace:
    Checklist → Decisions → Form generation pipeline.
    """

    case = get_object_or_404(Case, id=case_id)

    # ensure draft exists
    draft, _ = BylawDraft.objects.get_or_create(case=case)

    decisions = BylawDecision.objects.filter(is_active=True).order_by("sequence_order")

    if request.method == "POST":
        for decision in decisions:
            value = request.POST.get(decision.decision_code)

            if value:
                DecisionSession.objects.update_or_create(
                    draft=draft,
                    decision=decision,
                    defaults={"value": value}
                )

        return redirect(f"/case/{case.id}/stage/{stage_code}/form/")

    context = {
        "case": case,
        "stage_code": stage_code,
        "decisions": decisions
    }

    return render(request, "core/decision_workspace.html", context)


