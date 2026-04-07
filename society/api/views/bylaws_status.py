from rest_framework.decorators import api_view
from rest_framework.response import Response
from statutory.models import SocietyBylaws


@api_view(["GET"])
def bylaws_status(request):
    society_id = request.GET.get("society_id")

    doc = SocietyBylaws.objects.filter(
        society_id=society_id
    ).order_by("-version_number").first()

    if not doc:
        return Response({"status": "NONE"})

    return Response({
        "status": doc.status.upper(),  # 🔥 IMPORTANT
        "version": doc.version_number
    })