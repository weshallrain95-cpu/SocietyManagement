from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from society.models import SocietyMember
from datetime import date

from society.models import Flat, FlatOwnership


@api_view(["GET"])
def get_ownership(request):
    flat_id = request.GET.get("flat_id")

    if not flat_id:
        return Response({"error": "flat_id required"}, status=400)

    flat = get_object_or_404(Flat, id=flat_id)

    ownership = FlatOwnership.objects.filter(
        flat=flat,
        is_active=True
    ).first()

    if not ownership:
        return Response([])

    owners = ownership.owners.all()

    data = []

    for o in owners:
        data.append({
            "name": o.person.full_name if o.person else o.legal_entity_name,
            "phone": o.person.phone if o.person else "",
            "person_id": o.person.id,   # ✅ CRITICAL ADD
            "percentage": float(o.ownership_percentage),
        })

    return Response(data)

    from django.db import transaction
from society.models import FlatOwner, Person


@api_view(["POST"])
def update_ownership(request):
    flat_id = request.data.get("flat_id")
    owners = request.data.get("owners", [])

    flat = get_object_or_404(Flat, id=flat_id)

    ownership = FlatOwnership.objects.filter(
        flat=flat,
        is_active=True
    ).first()

    if not ownership:
        return Response({"error": "No ownership found"}, status=400)

    total = sum([float(o.get("percentage", 0)) for o in owners])

    if abs(total - 100) > 0.001:
        return Response({"error": "Total must be 100%"}, status=400)

    with transaction.atomic():

        # 🔥 DELETE OLD OWNERS
        FlatOwner.objects.filter(ownership=ownership).delete()

        # 🔥 CREATE NEW
        for o in owners:

            name = o.get("name")
            phone = o.get("phone")
            percentage = float(o.get("percentage"))

            from datetime import date
            from society.models import SocietyMember

            if phone:
                person, _ = Person.objects.get_or_create(
                    phone=phone,
                    defaults={"full_name": name}
                )

                # ✅ ENSURE OWNER IS SOCIETY MEMBER
                if phone:
                    person, _ = Person.objects.get_or_create(
                        phone=phone,
                        defaults={"full_name": name}
                    )
                else:
                    person = Person.objects.create(
                        full_name=name
                    )

                # ✅ CHECK IF MEMBER EXISTS
                member = SocietyMember.objects.filter(
                    society_id=flat.society_id,
                    person_id=person.id,
                    is_active=True
                ).first()

                # ✅ ONLY CREATE IF NEW PERSON
                if not member:
                    last_member = SocietyMember.objects.filter(
                        society_id=flat.society_id
                    ).order_by("-member_number").first()

                    if last_member and last_member.member_number:
                        last_num = int(last_member.member_number.replace("M", ""))
                        next_number = last_num + 1
                    else:
                        next_number = 1

                    member_number = f"M{str(next_number).zfill(4)}"

                    SocietyMember.objects.create(
                        society_id=flat.society_id,
                        person_id=person.id,
                        membership_type="REGULAR",
                        is_active=True,
                        admitted_on=date.today(),
                        member_number=member_number,
                    )

                FlatOwner.objects.create(
                    ownership=ownership,
                    person=person,
                    ownership_percentage=percentage
                )

            else:
                FlatOwner.objects.create(
                    ownership=ownership,
                    legal_entity_name=name,
                    ownership_percentage=percentage
                )

    return Response({"status": "updated"})