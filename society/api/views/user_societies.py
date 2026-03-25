from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import Person, SocietyMember

@api_view(["GET"])
def get_user_societies(request):
    mobile = request.GET.get("mobile")

    if not mobile:
        return Response({"error": "Mobile required"}, status=400)

    try:
        person = Person.objects.get(phone=mobile)
    except Person.DoesNotExist:
        return Response({"societies": []})

    memberships = SocietyMember.objects.filter(
        person=person,
        is_active=True
    ).select_related("society")

    societies = []

    for m in memberships:
        societies.append({
            "id": m.society.id,
            "name": m.society.name,
            "status": m.society.legal_status,
        })

    return Response({"societies": societies})
    