from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

import openpyxl

from society.models import Society, Flat, FlatOwnership


VALID_ENTITY_TYPES = ["INDIVIDUAL", "ENTITY", "SOCIETY"]


@api_view(["POST"])
def upload_ownership_excel(request):
    """
    STRICT OWNERSHIP INGESTION (PRODUCTION GRADE)

    Guarantees:
    ✔ No orphan flats
    ✔ No duplicate ownership
    ✔ Full coverage required
    ✔ Entity validation enforced
    ✔ % must be 100
    ✔ No re-upload allowed
    """

    file = request.FILES.get("file")
    society_id = request.data.get("society_id")

    if not file:
        return Response({"error": "Excel file required"}, status=400)

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # 🚫 BLOCK RE-UPLOAD
    existing_global = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).exists()

    if existing_global:
        return Response({
            "status": "failed",
            "message": "Ownership already exists. Use transfer flow.",
        }, status=400)

    wb = openpyxl.load_workbook(file)
    ws = wb.active

    errors = []
    processed_flats = set()
    upload_data = []

    # ---------- STEP 1: PARSE + VALIDATE FILE ----------
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):

        try:
            (
                society_id_cell,
                wing,
                floor,
                flat_no,
                owner_name,
                phone,
                percentage,
                entity,
            ) = row

            if not flat_no:
                errors.append(f"Row {i}: Flat No missing")
                continue

            flat_no = str(flat_no).strip()

            # ---------- FLAT EXISTS ----------
            flat = Flat.objects.filter(
                society=society,
                flat_number=flat_no
            ).first()

            if not flat:
                errors.append(f"Row {i}: Flat not found ({flat_no})")
                continue

            # ---------- ENTITY ----------
            if not entity or str(entity).upper() not in VALID_ENTITY_TYPES:
                errors.append(f"Row {i}: Invalid entity")
                continue

            entity = str(entity).upper()

            # ---------- OWNER ----------
            if entity != "SOCIETY" and not owner_name:
                errors.append(f"Row {i}: Owner name required for {flat_no}")
                continue

            # ---------- % ----------
            if not percentage or float(percentage) != 100:
                errors.append(f"Row {i}: Ownership % must be 100 ({flat_no})")
                continue

            # ---------- DUPLICATE IN FILE ----------
            if flat_no in processed_flats:
                errors.append(f"Row {i}: Duplicate flat in file ({flat_no})")
                continue

            processed_flats.add(flat_no)

            upload_data.append({
                "flat": flat,
                "flat_no": flat_no,
                "entity": entity,
                "owner_name": owner_name,
            })

        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    # ---------- STEP 2: FULL COVERAGE CHECK ----------
    db_flats = set(
        Flat.objects.filter(society=society)
        .values_list("flat_number", flat=True)
    )

    uploaded_flats = set(processed_flats)

    missing = db_flats - uploaded_flats
    extra = uploaded_flats - db_flats

    if missing:
        return Response({
            "status": "failed",
            "message": "Missing ownership for some flats",
            "missing_flats": list(missing)[:20],
            "errors": errors,
        }, status=400)

    if extra:
        return Response({
            "status": "failed",
            "message": "Invalid flats in upload",
            "extra_flats": list(extra)[:20],
            "errors": errors,
        }, status=400)

    if errors:
        return Response({
            "status": "failed",
            "errors": errors,
        }, status=400)

    # ---------- STEP 3: CREATE OWNERSHIP ----------
    created = 0

    with transaction.atomic():

        for item in upload_data:

            FlatOwnership.objects.create(
                flat=item["flat"],
                is_active=True,
            )

            created += 1

    # ---------- FINAL SAFETY CHECK ----------
    total_flats = Flat.objects.filter(society=society).count()
    total_ownerships = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).count()

    if total_flats != total_ownerships:
        return Response({
            "status": "failed",
            "message": "Post-check failed: mismatch in flats vs ownership",
            "total_flats": total_flats,
            "ownerships": total_ownerships,
        }, status=500)

    return Response({
        "status": "completed",
        "created_records": created,
        "total_flats": total_flats,
    })