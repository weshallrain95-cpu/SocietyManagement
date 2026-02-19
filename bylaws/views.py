from django.http import JsonResponse
from django.views import View
from bylaws.models import BylawVersion

class BylawsVersionExportView(View):
    def get(self, request, code):
        try:
            version = BylawVersion.objects.get(code=code)
        except BylawVersion.DoesNotExist:
            return JsonResponse({"error": "version not found"}, status=404)

        data = {"code": version.code, "title": version.title, "chapters": []}
        for ch in version.chapters.all().order_by("chapter_number"):
            chd = {"chapter_number": ch.chapter_number, "title": ch.title, "sequence_order": ch.sequence_order, "clauses": []}
            for cl in ch.clauses.all().order_by("sequence_order"):
                cld = {"clause_number": cl.clause_number, "title": cl.title, "legal_text": cl.legal_text, "sequence_order": cl.sequence_order, "sub_clauses": []}
                for sub in cl.sub_clauses.all().order_by("sequence_order"):
                    cld["sub_clauses"].append({
                        "sub_clause_number": sub.sub_clause_number,
                        "legal_text": sub.legal_text,
                        "sequence_order": sub.sequence_order
                    })
                chd["clauses"].append(cld)
            data["chapters"].append(chd)
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})

from django.views.generic import TemplateView

from django.shortcuts import render, redirect

def bylaws_viewer(request):
    if request.method == "POST":
        name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        role = request.POST.get("role")

        request.session["initiator"] = {
            "name": name,
            "phone": phone,
            "role": role,
        }

        return redirect("/bylaws/step-2/")

    return render(request, "Documents/bylaws/viewer.html")

from django.shortcuts import render, get_object_or_404, redirect
from society.models import Case
from .models import BylawDraft


def start_bylaws_engine(request, case_id):
    case = get_object_or_404(Case, id=case_id)

    draft, created = BylawDraft.objects.get_or_create(case=case)

    return redirect(f"/bylaws/draft/{draft.id}/")

def bylaws_draft_workspace(request, draft_id):
    draft = get_object_or_404(BylawDraft, id=draft_id)

    context = {
        "draft": draft
    }

    return render(request, "Documents/bylaws/draft_workspace.html", context)

