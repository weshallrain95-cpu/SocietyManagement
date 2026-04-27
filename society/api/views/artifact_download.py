from rest_framework.decorators import api_view
from django.http import FileResponse
from statutory.models import SocietyLegalDocument
from society.models import Society
from datetime import datetime


@api_view(["GET"])
def download_artifact(request):
    society_id = request.GET.get("society_id")
    code = request.GET.get("artifact_code")

    doc = SocietyLegalDocument.objects.filter(
        society_id=society_id,
        template__artifact_code=code
    ).first()

    if not doc or not doc.file:
        return FileResponse(status=404)

    society = Society.objects.get(id=society_id)
    date_str = datetime.now().strftime("%d-%m-%Y")

    filename = f"{society.name.replace(' ', '')}-{code}-{date_str}.txt"

    response = FileResponse(doc.file.open(), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response