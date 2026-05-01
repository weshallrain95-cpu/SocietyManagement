from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from society.models import Society



@api_view(["POST"])
def update_registration(request):

    print("RAW BODY:", request.body)
    print("PARSED DATA:", request.data)
    
    society_id = request.data.get("society_id")
    registration_number = request.data.get("registration_number")
    registration_date = request.data.get("registration_date")

    if not registration_number or not registration_date:
        return Response(
            {"error": "registration_number and registration_date required"},
            status=400
    )

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    try:
        society = Society.objects.get(id=society_id)
    except Society.DoesNotExist:
        return Response({"error": "Society not found"}, status=404)

    # ✅ Update fields
    society.registration_number = registration_number
    society.registration_date = registration_date
    society.legal_status = "REGISTERED"
    
    print("FINAL VALUES:", registration_number, registration_date)
    print("SOCIETY ID:", society_id)
    print("FOUND SOCIETY:", society.id)
    
    society.save()

    print("DEBUG:", request.data)

    return Response({
        "message": "Registration updated successfully"
    }, status=status.HTTP_200_OK)