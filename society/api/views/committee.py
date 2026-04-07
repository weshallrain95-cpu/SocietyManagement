from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from society.models import (
    Committee,
    CommitteeMembership,
    SocietyMember,
    SocietyOfficeBearer,
)

# ================= BASIC CREATE (KEEP EXISTING) =================
@api_view(["POST"])
def create_committee(request):
    society_id = request.data.get("society_id")
    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")

    committee = Committee.objects.create(
        society_id=society_id,
        start_date=start_date,
        end_date=end_date,
    )

    return Response({
        "id": committee.id,
        "start_date": committee.start_date,
        "end_date": committee.end_date,
    })


# ================= FULL GOVERNANCE CREATE =================
@api_view(["POST"])
def create_full_committee(request):
    data = request.data

    society_id = data.get("society_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    members = data.get("members", [])

    # -------- VALIDATION --------
    if not start_date:
        return Response({"error": "Start date required"}, status=400)

    if not end_date:
        return Response({"error": "End date required"}, status=400)

    if len(members) < 3:
        return Response({"error": "Minimum 3 members required"}, status=400)

    roles = [m.get("role") for m in members]

    if "CHAIRMAN" not in roles:
        return Response({"error": "Chairman required"}, status=400)

    if "SECRETARY" not in roles:
        return Response({"error": "Secretary required"}, status=400)

    if "TREASURER" not in roles:
        return Response({"error": "Treasurer required"}, status=400)

    try:
        with transaction.atomic():

            # ================= DEACTIVATE EXISTING COMMITTEE =================
            Committee.objects.filter(
                society_id=society_id,
                is_active=True
            ).update(is_active=False)

            # ================= CREATE NEW COMMITTEE =================
            committee = Committee.objects.create(
                society_id=society_id,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
            )

            created_members = []

            # ================= DEACTIVATE OLD MEMBERSHIPS =================
            CommitteeMembership.objects.filter(
                society_id=society_id,
                is_active=True
            ).update(is_active=False)

            # ================= CREATE NEW MEMBERS =================
            for m in members:
                person_id = m.get("person_id")
                role = m.get("role")

                if not person_id:
                    raise Exception("person_id missing")

                if not role:
                    raise Exception("role missing")

                # Resolve SocietyMember
                member = SocietyMember.objects.get(
                    society_id=society_id,
                    person_id=person_id,
                    is_active=True,
                )

                # Create CommitteeMembership
                cm = CommitteeMembership.objects.create(
                    society_id=society_id,
                    member=member,
                    committee=committee,
                    elected_on=start_date,
                    term_end=end_date,
                    is_active=True,
                )

                created_members.append(cm.id)

                # ================= OFFICE BEARER HANDLING =================
                if role in ["CHAIRMAN", "SECRETARY", "TREASURER"]:

                    # Deactivate existing active role
                    SocietyOfficeBearer.objects.filter(
                        society_id=society_id,
                        role=role,
                        is_active=True
                    ).update(is_active=False)

                    # Create new office bearer
                    SocietyOfficeBearer.objects.create(
                        society_id=society_id,
                        committee_membership_ref=cm,
                        user=member.person.user if member.person.user else None,
                        role=role,
                        appointed_on=start_date,
                        term_end=end_date,
                        is_active=True,
                    )

        from society.models import Society

        society = Society.objects.get(id=society_id)
        society.onboarding_stage = "OPERATIONS_PENDING"
        society.save()
        
        return Response({
            "message": "Committee created successfully",
            "committee_id": committee.id,
            "members_created": created_members,
        })

    except SocietyMember.DoesNotExist:
        return Response(
            {"error": "SocietyMember not found for given person"},
            status=400,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=400)