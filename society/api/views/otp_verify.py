from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from society.models import Person, SocietyMember


@api_view(["POST"])
def verify_otp(request):
    mobile = request.data.get("mobile")
    otp = request.data.get("otp")

    print("DEBUG OTP:", otp, type(otp))

    # ✅ STEP 0 — OTP VALIDATION
    if str(otp) != "123456":
        return Response(
            {"error": "Invalid OTP"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ==========================================================
    # STEP 1 — RESOLVE PERSON (SUPPORT CREATE + LOGIN)
    # ==========================================================
    person = Person.objects.filter(phone=mobile).first()

    # 🟠 CREATE FLOW (NEW USER)
    if not person:
        return Response({
            "message": "OTP verified",
            "user": None,
            "societies": []
        })

    # ==========================================================
    # STEP 2 — FETCH SOCIETIES (LOGIN FLOW)
    # ==========================================================
    memberships = (
        SocietyMember.objects
        .filter(person=person)
        .select_related("society")
    )

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
        except Exception:
            onboarding = {
                "stage": "SOCIETY_SETUP",
                "readiness": {}
            }

        societies.append({

            "id": society.id,

            "name": society.name,

            "registration_number":
                society.registration_number,

            "registration_date":
                society.registration_date,

            "legal_status":
                society.legal_status,

            "onboarding": onboarding,
        })

    # ==========================================================
    # STEP 3 — RESPONSE (LOGIN FLOW)
    # ==========================================================
    return Response({
        "message": "OTP verified",
        "user": {
            "id": person.id,
            "name": person.full_name,
            "mobile": person.phone
        },
        "societies": societies
    })
    