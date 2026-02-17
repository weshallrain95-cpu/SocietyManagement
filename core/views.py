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


from django.shortcuts import redirect, get_object_or_404, render
from django.db import transaction
from society.models import Person, Case, CaseStage
import traceback

def case_create(request):
    print("DEBUG: entered case_create")   # <- runtime trace
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        print(f"DEBUG: payload name={name} phone={phone}")

        try:
            with transaction.atomic():
                person, created = Person.objects.get_or_create(
                    phone=phone,
                    defaults={"full_name": name or "unknown"}
                )
                print(f"DEBUG: person id={person.id} created={created}")

                existing_case = Case.objects.filter(
                    initiated_by=person,
                    case_type="prereg",
                    status="initiated"
                ).first()
                print(f"DEBUG: existing_case = {existing_case}")

                if existing_case:
                    print("DEBUG: redirecting to existing case")
                    return redirect(f"/case/{existing_case.id}/")

                new_case = Case.objects.create(
                    initiated_by=person,
                    case_type="prereg",
                    status="initiated"
                )
                print(f"DEBUG: created new_case id={new_case.id}")

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

                created_count = 0
                for stage in STAGES:
                    cs = CaseStage.objects.create(
                        case=new_case,
                        stage_code=stage,
                        status="pending"
                    )
                    created_count += 1
                    print(f"DEBUG: created CaseStage id={cs.id} code={cs.stage_code}")

                print(f"DEBUG: created {created_count} stages for case {new_case.id}")
            # commit occurs here
            return redirect(f"/case/{new_case.id}/")

        except Exception as exc:
            print("ERROR: exception during case_create")
            print(traceback.format_exc())
            return render(request, "core/error.html", {"error": str(exc)})
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



