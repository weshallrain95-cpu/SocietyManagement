from rest_framework.decorators import api_view
from rest_framework.response import Response
from society.models import Person

@api_view(["GET"])
def mobile_exists(request):
    mobile = request.GET.get("mobile")

    exists = Person.objects.filter(phone=mobile).exists()

    return Response({
        "mobile_exists": exists
    })
