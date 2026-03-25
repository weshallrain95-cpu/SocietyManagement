from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Person, SocietyMember


@api_view(["POST"])
def verify_otp(request):
    mobile = request.data.get("mobile")
    otp = request.data.get("otp")

    print("DEBUG OTP:", otp, type(otp))

    # ✅ TEMP OTP
    if str(otp) != "123456":
        return Response(
            {"error": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ STEP 1 — FIND USER
    try:
        person = Person.objects.get(phone=mobile)
    except Person.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ STEP 2 — GET SOCIETIES
    memberships = SocietyMember.objects.filter(person=person).select_related("society")

    societies = []

    for m in memberships:
        society = m.society

        # ✅ SAFE TRACKER ACCESS
        try:
            tracker = society.soft_onboarding_tracker

            onboarding = {
                "stage": tracker.get_onboarding_stage(),
                "readiness": tracker.readiness_snapshot(),
            }

        except:
            onboarding = {
                "stage": "SOCIETY_SETUP",
                "readiness": {}
            }

        societies.append({
            "id": society.id,
            "name": society.name,
            "onboarding": onboarding
        })

    # ✅ STEP 3 — RESPONSE
    return Response({
        "message": "OTP verified",
        "user": {
            "id": person.id,
            "name": person.full_name,
            "mobile": person.phone
        },
        "societies": societies
    })
    