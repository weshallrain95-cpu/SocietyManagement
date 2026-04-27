from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse

import os

from society.models import Society
from statutory.document_engine.bylaw_generator import BylawDocumentGenerator


# =============================
# GENERATE BYLAWS
# =============================
@api_view(["POST"])
def generate_bylaws(request):

    print("🔥 RECEIVED HOOKS:", request.data)

    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    society_data = {
        "society_name": society.name,
        "registration_number": society.registration_number,
        "registered_address": request.data.get("registered_address") 
            or getattr(society, "address", "N/A"),
        "district": society.district,
        "adoption_date": request.data.get("adoption_date"),
    }

    hooks = {
        "share_value": 50,
        "minimum_shares_per_member": 10,
        "entrance_fee": 100,
        "maintenance_charge_basis": "flat_area",
        "sinking_fund_percent": 0.25,
        "repair_fund_percent": 0.75,
        "late_payment_interest_percent": 18,
        "non_occupancy_charge_percent": 10,
        "committee_size": 11,
        "committee_term_years": 5,
        "quorum_general_body_percent": 25,
        "redevelopment_consent_percent": 75,
    }

    try:
        document_text = BylawDocumentGenerator.generate(
            society_data=society_data,
            hooks=hooks
        )

        import os
        from datetime import datetime

        # 🔥 BASE PATH
        base_dir = "/tmp/bylaws"

        # 🔥 CLEAN NAME (no spaces issues)
        society_name = society.name.replace(" ", "_")

        # 🔥 VERSIONING (simple v1 for now)
        version = "v1"

        # 🔥 DATE
        date_str = datetime.now().strftime("%Y-%m-%d")

        # 🔥 FINAL PATH
        dir_path = os.path.join(base_dir, society_name, version)
        os.makedirs(dir_path, exist_ok=True)

        file_path = os.path.join(dir_path, f"{date_str}.txt")

        # 🔥 SAVE FILE
        with open(file_path, "w") as f:
            f.write(document_text)

        from statutory.models import SocietyBylaws

        # 🔥 GET NEXT VERSION
        latest = SocietyBylaws.objects.filter(
            society=society
        ).order_by("-version_number").first()

        next_version = 1 if not latest else latest.version_number + 1

        # 🔥 SAVE TO DB
        SocietyBylaws.objects.create(
            society=society,
            version_number=next_version,
            generated_document_path=file_path,
            governance_hooks_json=request.data.get("governance_hooks", {}),
            status="GENERATED"
        )
        
        return Response({
            "status": "success",
            "message": "Bylaws generated",
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

# =============================
# DOWNLOAD BYLAWS
# =============================
@api_view(["GET"])
def download_bylaws(request):
    society_id = request.GET.get("society_id")

    import os

    base_dir = "/tmp/bylaws"
    society_name = Society.objects.get(id=society_id).name.replace(" ", "_")
    version = "v1"

    dir_path = os.path.join(base_dir, society_name, version)

    if not os.path.exists(dir_path):
        return Response({"error": "No bylaws found"}, status=404)

    # 🔥 GET LATEST FILE
    files = sorted(os.listdir(dir_path), reverse=True)

    if not files:
        return Response({"error": "No files found"}, status=404)

    latest_file = files[0]
    file_path = os.path.join(dir_path, latest_file)

    from datetime import datetime

    society = Society.objects.get(id=society_id)

    # 🔥 FORMAT NAME
    date_str = datetime.now().strftime("%d-%m-%Y")

    filename = f"{society.name.replace(' ', '')}-Bylaws-Ver1.0-{date_str}.txt"

    response = FileResponse(open(file_path, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response

    if not os.path.exists(file_path):
        return Response(
            {"error": "File not found. Generate first."},
            status=404
        )

    from datetime import datetime

    society = Society.objects.get(id=society_id)

    # 🔥 FORMAT NAME
    date_str = datetime.now().strftime("%d-%m-%Y")

    filename = f"{society.name.replace(' ', '')}-Bylaws-Ver1.0-{date_str}.txt"

    response = FileResponse(open(file_path, "rb"), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
