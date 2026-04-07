from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import SocietyMember

@api_view(["GET"])
def list_members(request):
    society_id = request.GET.get("society_id")

    members = SocietyMember.objects.filter(
        society_id=society_id,
        is_active=True
    ).select_related("person")

    data = [
        {
            "id": m.id,
            "name": m.person.full_name,
            "phone": m.person.phone,
            "member_number": m.member_number,
        }
        for m in members
    ]

    return Response(data)