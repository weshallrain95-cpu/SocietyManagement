from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from statutory.preregistration.registrar_pack import generate_registrar_pack
from django.views.decorators.csrf import csrf_exempt

from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from society.models import Society
from statutory.control_room_engine import ControlRoomEngine

from society.models import Society
from statutory.services import (
    get_next_legal_step,
    compute_risk,
    complete_current_step,
    finalize_society_if_allowed,
)

@api_view(["GET"])
def next_legal_step(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    progress = get_next_legal_step(society)

    if progress is None:
        return Response(
            {
                "society": society.name,
                "message": "All legal stages completed",
                "status": "COMPLETED",
                "risk": "GREEN",
            },
            status=status.HTTP_200_OK,
        )

    risk = compute_risk(progress)

    return Response(
        {
            "society": society.name,
            "stage": progress.legal_stage.name,
            "status": progress.status,
            "risk": risk,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def complete_legal_step(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    completed, next_step = complete_current_step(society)

    if completed is None:
        return Response(
            {
                "society": society.name,
                "message": "All legal stages already completed",
            },
            status=status.HTTP_200_OK,
        )

    response = {
        "society": society.name,
        "completed_stage": completed.legal_stage.name,
    }

    if next_step:
        response["next_stage"] = next_step.legal_stage.name
        response["status"] = "IN_PROGRESS"
    else:
        response["status"] = "COMPLETED"

    return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def finalize_society_completion(request, society_id):
    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response(
            {"detail": "No Society matches the given query."},
            status=status.HTTP_404_NOT_FOUND,
        )

    allowed, reason = finalize_society_if_allowed(society)

    if not allowed:
        return Response(
            {
                "society": society.name,
                "status": "NOT_FINALIZED",
                "reason": reason,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "society": society.name,
            "status": "LEGALLY_COMPLETED",
            "message": "Society legally finalized with all mandatory documents",
        },
        status=status.HTTP_200_OK,
    )

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from society.models import Society
from statutory.preregistration.snapshot import preregistration_readiness_snapshot

def preregistration_snapshot_view(request, society_id):
    """
    Society-aware preregistration snapshot endpoint.
    """

    society = get_object_or_404(Society, id=society_id)

    snapshot = preregistration_readiness_snapshot(society)

    return JsonResponse(snapshot, status=200)

    snapshot = preregistration_readiness_snapshot(society)
    return JsonResponse(snapshot, status=200)

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from statutory.preregistration.actions import complete_obligation
from statutory.preregistration.snapshot import preregistration_readiness_snapshot
from society.models import Society
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update_preregistration_obligation_status(request, obligation_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    import json
    data = json.loads(request.body)

    society_id = data.get("society_id")
    new_status = data.get("status")

    if not society_id or not new_status:
        return JsonResponse({"error": "Missing parameters"}, status=400)

    from statutory.models import SocietyObligationStatus
    from society.models import Society
    from statutory.models import LegalObligation

    society = Society.objects.filter(id=society_id).first()
    obligation = LegalObligation.objects.filter(id=obligation_id).first()

    if not society or not obligation:
        return JsonResponse({"error": "Invalid society or obligation"}, status=404)

    status_obj, created = SocietyObligationStatus.objects.get_or_create(
        society=society,
        legal_obligation=obligation,
        defaults={"status": new_status},
    )

    if not created:
        status_obj.status = new_status
        status_obj.save()

    return JsonResponse({
        "success": True,
        "status": status_obj.status,
    })


from django.http import JsonResponse
from society.models import Society


def societies_list_view(request):
    societies = Society.objects.all().values("id", "name")

    return JsonResponse({
        "societies": list(societies)
    })

# statutory/api.py (append or add near other views)

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from statutory.preregistration.registrar_pack import generate_registrar_pack

from statutory.models import SocietyLegalDocument, LegalArtifactTemplate
from society.models import Society

@csrf_exempt  # DEV ONLY: remove this in production and use proper CSRF/session
@require_POST
def upload_preregistration_document(request):
    """
    Expected form-data:
      - society_id (int)
      - template_id (int)
      - file (file)
    Returns JSON with the created document info or 400 on missing params.
    """
    society_id = request.POST.get("society_id")
    template_id = request.POST.get("template_id")
    uploaded_file = request.FILES.get("file")

    if not society_id or not template_id or not uploaded_file:
        return HttpResponseBadRequest("Missing society_id, template_id or file")

    # validate models exist
    society = get_object_or_404(Society, id=society_id)
    template = get_object_or_404(LegalArtifactTemplate, id=template_id)

    # create SocietyLegalDocument. Field names: template, file, status, uploaded_at
    doc = SocietyLegalDocument.objects.create(
        society=society,
        template=template,
        file=uploaded_file,
        status="SIGNED"  # or whatever initial status is appropriate
    )

    return JsonResponse({
        "id": doc.id,
        "society_id": doc.society_id,
        "template_id": template.id,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
    }, status=201)

from django.http import JsonResponse
from society.models import Society


def registrar_pack_view(request, society_id):
    society = Society.objects.filter(id=society_id).first()

    if not society:
        return JsonResponse({"error": "Society not found"}, status=404)

    data = generate_registrar_pack(society)
    return JsonResponse(data, status=200)

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from statutory.models import SocietyLegalDocument

@csrf_exempt
@require_POST
def delete_preregistration_document(request):
    """
    Deletes an uploaded preregistration document.

    Expected POST body:
    {
        "template_id": int
    }
    """

    template_id = request.POST.get("template_id") or request.GET.get("template_id")

    if not template_id:
        return JsonResponse({"error": "template_id required"}, status=400)

    deleted, _ = SocietyLegalDocument.objects.filter(template_id=template_id).delete()

    if deleted == 0:
        return JsonResponse({"error": "Document not found"}, status=404)

    return JsonResponse({"success": True})

from django.http import HttpResponse
from statutory.preregistration.pack_builder import build_registrar_pack

def registrar_pack_download_view(request, society_id):
    society = Society.objects.get(id=society_id)

    snapshot = preregistration_readiness_snapshot(society)
    if not snapshot["registrar_ready"]:
        return HttpResponse(
            "Registrar pack not ready",
            status=400
        )

    pack_bytes = build_registrar_pack(society)

    response = HttpResponse(pack_bytes, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="registrar_pack_society_{society_id}.zip"'
    return response

# Paste-safe replacement for submit_to_registrar
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction

# Prefer the explicit, stable import (avoid fragile re-exports)
from statutory.preregistration.snapshot import preregistration_readiness_snapshot

from statutory.models import RegistrarSubmission
from society.models import Society


@csrf_exempt         # dev only; remove in production
@require_POST
@transaction.atomic
def submit_to_registrar(request, society_id):
    """
    Conservative, safe submission handler.

    - Locks the society row to avoid concurrent duplicate SUBMITTED entries.
    - Uses explicit preregistration snapshot import from statutory.preregistration.
    - Returns JSON with an explicit ISO timestamp.
    """

    # 1) Load society (fail fast)
    try:
        # Lock the society row for the duration of this transaction to serialize submissions
        society = Society.objects.select_for_update().get(id=society_id)
    except Society.DoesNotExist:
        return JsonResponse({"error": "Society not found"}, status=404)

    # 2) Read readiness snapshot (explicit stable import)
    snapshot = preregistration_readiness_snapshot(society)
    if not snapshot.get("registrar_ready"):
        return JsonResponse({"error": "Society not registrar ready"}, status=400)

    # 3) Prevent double submission (safe under select_for_update lock)
    already = RegistrarSubmission.objects.filter(
        society=society,
        status="SUBMITTED"
    ).exists()

    if already:
        return JsonResponse({"error": "Already submitted"}, status=400)

    # 4) Create submission
    # Use more robust hash if you want stable cross-process results (optionally swap later)
    snapshot_hash = str(hash(str(snapshot)))

    submission = RegistrarSubmission.objects.create(
        society=society,
        submitted_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
        snapshot_hash=snapshot_hash,
        submitted_at=timezone.now(),
        status="SUBMITTED",
    )

    # 5) Return explicit ISO timestamp (clear for clients)
    return JsonResponse({
        "message": "Submitted successfully",
        "submitted_at": submission.submitted_at.isoformat(),
    })

@csrf_exempt
def create_society_structure(request, society_id):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    import json
    from society.services.structure_generator import generate_society_structure

    data = json.loads(request.body)

    society = Society.objects.get(id=society_id)

    result = generate_society_structure(
        society=society,
        total_wings=data["total_wings"],
        floors_per_wing=data["floors_per_wing"],
        flats_per_floor=data["flats_per_floor"],
        flat_numbering_style=data.get("flat_numbering", "A-101"),
        carpet_area=data.get("carpet_area"),
    )

    return JsonResponse({
        "success": True,
        "structure": result
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def control_room_overview(request):

    engine = ControlRoomEngine()

    snapshot = engine.build_overview()

    return Response(snapshot)