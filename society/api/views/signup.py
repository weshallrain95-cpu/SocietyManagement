from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from society.models import Society, Person, Wing, Floor, Flat, SocietyMember


@api_view(["POST"])
def signup_create_society(request):

    data = request.data

    name = data.get("name")
    mobile = data.get("mobile")
    email = data.get("email")

    society_name = data.get("society_name")
    state = data.get("state")
    district = data.get("district")

    designation = data.get("designation")

    wing_name = data.get("wing")
    floor_number = data.get("floor")
    flat_number = data.get("flat_number")
    flat_type = data.get("flat_type")
    flat_area = data.get("flat_area")

    society_status = data.get("society_status")
    registration_number = data.get("registration_number")
    registration_date = data.get("registration_date")

    # STEP 1A — check registration number uniqueness
    if registration_number:
        if Society.objects.filter(registration_number=registration_number).exists():
            return Response(
                {"error": "Registration number already exists"},
                status=400
            )

    # STEP 1 — get or create person
    person, created = Person.objects.get_or_create(
        phone=mobile,
        defaults={
            "full_name": name,
            "email": email,
        }
    )

    # 🔒 ATOMIC TRANSACTION START
    with transaction.atomic():

        society = Society.objects.create(
            name=society_name,
            state_code=state,
            district=district,
            legal_status=society_status,
            registration_number=registration_number,
            registration_date=registration_date,
        )

        # ✅ CREATE STRUCTURE ONLY IF BASIC DATA EXISTS
        if wing_name and flat_number:

            wing = Wing.objects.create(
                society=society,
                name=wing_name
            )

            floor = None
            if floor_number:
                floor = Floor.objects.create(
                    wing=wing,
                    number=floor_number
                )

            flat = Flat.objects.create(
                society=society,
                wing=wing,
                floor=floor_number if floor_number else None,
                floor_ref=floor,
                flat_number=flat_number,
                flat_type=flat_type,
                carpet_area_sqft=flat_area,
            )

            # LINK MEMBER TO SOCIETY
            from datetime import date

            SocietyMember.objects.create(
                society=society,
                person=person,
                membership_type="PROMOTER",
                admitted_on=date.today(),
                is_active=True
            )

        else:
            # ✅ STILL CREATE MEMBER WITHOUT FLAT
            from datetime import date

            SocietyMember.objects.create(
                society=society,
                person=person,
                membership_type="PROMOTER",
                admitted_on=date.today(),
                is_active=True
            )

    # 🔒 ATOMIC TRANSACTION END

    return Response(
        {
            "message": "Society created successfully",
            "society_id": society.id
        },
        status=status.HTTP_201_CREATED,
    )


