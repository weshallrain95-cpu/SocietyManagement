from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from openpyxl import load_workbook
from datetime import date
from society.models import SocietyMember

from society.models import Society, Flat, FlatOwnership, FlatOwner, Person


VALID_ENTITY_TYPES = ["INDIVIDUAL", "ENTITY", "SOCIETY"]


@api_view(["POST"])
def upload_ownership_excel(request):
    """
    Strict ownership ingestion (production grade).

    Guarantees:
    - No orphan flats
    - No duplicate ownership
    - Full coverage required
    - Entity validation enforced
    - Ownership % must be 100
    - No re-upload allowed
    - Atomic write (all or nothing)
    """

    file_obj = request.FILES.get("file")
    society_id = request.data.get("society_id")

    # ---------- BASIC VALIDATION ----------
    if not file_obj:
        return Response({"error": "Excel file required"}, status=400)

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ---------- BLOCK RE-UPLOAD ----------
    if FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).exists():
        return Response({
            "status": "failed",
            "message": "Ownership already exists. Use transfer flow."
        }, status=400)

    # ---------- LOAD EXCEL ----------
    try:
        workbook = load_workbook(file_obj)
        worksheet = workbook.active
    except Exception:
        return Response({
            "status": "failed",
            "message": "Invalid Excel file"
        }, status=400)

    errors = []
    processed_flats = set()
    upload_data = []

    rows = list(worksheet.iter_rows(min_row=2, values_only=True))

    # ---------- PARSE + VALIDATE ----------
    for index, row in enumerate(rows, start=2):

        try:
            if not row or len(row) < 10:
                errors.append(f"Row {index}: Invalid row format")
                continue

            # SAFE EXTRACTION
            flat_no_raw = row[3]
            owner_name_raw = row[6]
            phone_raw = row[7]
            percentage_raw = row[8]
            entity_raw = row[9]

            # NORMALIZATION
            flat_no = str(flat_no_raw).strip() if flat_no_raw else None
            owner_name = str(owner_name_raw).strip() if owner_name_raw else None
            phone = str(phone_raw).strip() if phone_raw else None
            entity = str(entity_raw).strip().upper() if entity_raw else None

            # FLAT
            if not flat_no:
                errors.append(f"Row {index}: Flat No missing")
                continue

            flat = Flat.objects.filter(
                society=society,
                flat_number=flat_no
            ).first()

            if not flat:
                errors.append(f"Row {index}: Flat not found ({flat_no})")
                continue

            # ENTITY
            if entity not in VALID_ENTITY_TYPES:
                errors.append(f"Row {index}: Invalid entity ({entity})")
                continue

            # OWNER
            if entity != "SOCIETY" and not owner_name:
                errors.append(f"Row {index}: Owner name required ({flat_no})")
                continue

            # %
            if percentage_raw is None:
                errors.append(f"Row {index}: Ownership % missing ({flat_no})")
                continue

            try:
                percentage = float(str(percentage_raw).strip())
            except Exception:
                errors.append(f"Row {index}: Invalid % ({flat_no})")
                continue

            if abs(percentage - 100) > 0.001:
                errors.append(f"Row {index}: Ownership must be 100% ({flat_no})")
                continue

            # DUPLICATE
            if flat_no in processed_flats:
                errors.append(f"Row {index}: Duplicate flat in file ({flat_no})")
                continue

            processed_flats.add(flat_no)

            upload_data.append({
                "flat": flat,
                "owner_name": owner_name,
                "entity": entity,
                "phone": phone,
            })

        except Exception as e:
            errors.append(f"Row {index}: {str(e)}")

    # ---------- FULL COVERAGE ----------
    db_flats = set(
        Flat.objects.filter(society=society)
        .values_list("flat_number", flat=True)
    )

    uploaded_flats = set(processed_flats)

    if db_flats - uploaded_flats:
        return Response({
            "status": "failed",
            "message": "Missing ownership for some flats",
            "errors": errors
        }, status=400)

    if uploaded_flats - db_flats:
        return Response({
            "status": "failed",
            "message": "Invalid flats in upload",
            "errors": errors
        }, status=400)

    if errors:
        return Response({
            "status": "failed",
            "errors": errors
        }, status=400)

    # ---------- ATOMIC CREATE ----------
    created = 0

    with transaction.atomic():

        for item in upload_data:

            ownership = FlatOwnership.objects.create(
                flat=item["flat"],
                acquired_on=date.today(),
                is_active=True,
            )

            # ---------- OWNER CREATION ----------
            if item["entity"] == "INDIVIDUAL":

                if item["phone"]:
                    person, _ = Person.objects.get_or_create(
                        phone=item["phone"],
                        defaults={"full_name": item["owner_name"]}
                    )
                else:
                    person = Person.objects.create(
                        full_name=item["owner_name"]
                    )

                # ✅ CHECK FIRST (avoid duplicate creation)
                member = SocietyMember.objects.filter(
                    society_id=society.id,
                    person_id=person.id,
                    is_active=True
                ).first()

                if not member:
                    # 🔥 GENERATE MEMBER NUMBER
                    last_member = SocietyMember.objects.filter(
                        society_id=society.id
                    ).order_by("-member_number").first()

                    if last_member and last_member.member_number:
                        last_num = int(last_member.member_number.replace("M", ""))
                        next_number = last_num + 1
                    else:
                        next_number = 1

                    member_number = f"M{str(next_number).zfill(4)}"   # M0001, M0002...

                    SocietyMember.objects.create(
                        society_id=society.id,
                        person_id=person.id,
                        membership_type="REGULAR",
                        is_active=True,
                        admitted_on=date.today(),
                        member_number=member_number,   # ✅ CRITICAL FIX
                    )

                FlatOwner.objects.create(
                    ownership=ownership,
                    person=person,
                    ownership_percentage=100,
                )

            else:
                FlatOwner.objects.create(
                    ownership=ownership,
                    legal_entity_name=item["owner_name"],
                    ownership_percentage=100,
                )

            created += 1

        # FINAL CHECK
        total_flats = Flat.objects.filter(society=society).count()
        total_ownerships = FlatOwnership.objects.filter(
            flat__society=society,
            is_active=True
        ).count()

        if total_flats != total_ownerships:
            raise Exception("Mismatch in flats vs ownership")

        society.onboarding_stage = "OWNERSHIP_REFINEMENT_PENDING"
        society.save(update_fields=["onboarding_stage"])

    return Response({
        "status": "completed",
        "message": "Ownership uploaded successfully. Onboarding complete.",
        "created_records": created,
        "total_flats": total_flats
    })