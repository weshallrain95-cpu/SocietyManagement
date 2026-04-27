from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction

from society.models import (
    Society,
    Flat,
    FlatOwnership,
    FlatOwner,
    ShareCertificate,
    Committee,
)


# =========================================================
# PREVIEW API (SCR16)
# =========================================================
@api_view(["GET"])
def preview_share_certificates(request):

    society_id = request.GET.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ----------------------------
    # FETCH FLATS (OPTIMIZED)
    # ----------------------------
    flats = Flat.objects.filter(society=society).prefetch_related(
        "ownerships__owners__person"
    )

    preview_data = []

    # ----------------------------
    # DEFAULT GOVERNANCE VALUES
    # ----------------------------
    # TODO: Replace with bylaws hooks
    share_value = 50
    share_count_per_flat = 10

    for flat in flats:

        # Get active ownership (from prefetched data)
        ownership = next(
            (o for o in flat.ownerships.all() if o.is_active),
            None
        )

        if not ownership:
            continue

        owner_names = []

        for o in ownership.owners.all():
            if o.person:
                owner_names.append(o.person.full_name)
            else:
                owner_names.append(o.legal_entity_name)

        preview_data.append({
            "flat_id": flat.id,
            "flat_number": flat.flat_number,
            "owners": owner_names,
            "share_count": share_count_per_flat,
            "share_value": share_value,
        })

    return Response({
        "society_id": society.id,
        "preview": preview_data
    })


# =========================================================
# GENERATE API (DRAFT CERTIFICATES)
# =========================================================
@api_view(["POST"])
def generate_share_certificates(request):

    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ----------------------------
    # LOCK CHECK (CRITICAL)
    # ----------------------------
    has_structure = society.flats.exists()

    has_ownership = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).exists()

    has_committee = Committee.objects.filter(
        society=society,
        is_active=True
    ).exists()

    if not (has_structure and has_ownership and has_committee):
        return Response(
            {"error": "Step locked. Complete Structure, Ownership, and Committee first."},
            status=403
        )

    # ----------------------------
    # FETCH FLATS (OPTIMIZED)
    # ----------------------------
    flats = Flat.objects.filter(society=society).prefetch_related(
        "ownerships"
    )

    # ----------------------------
    # IDEMPOTENCY CHECK (STRONG)
    # ----------------------------
    existing_count = ShareCertificate.objects.filter(
        society=society
    ).count()

    total_flats = flats.count()

    if existing_count >= total_flats:
        return Response({
            "message": "Share certificates already generated",
            "status": "EXISTS"
        })

    # ----------------------------
    # DEFAULT GOVERNANCE VALUES
    # ----------------------------
    # TODO: Replace with bylaws hooks
    share_value = 50
    share_count_per_flat = 10

    created_count = 0

    # ----------------------------
    # GENERATE CERTIFICATES
    # ----------------------------
    with transaction.atomic():

        for flat in flats:

            ownership = next(
                (o for o in flat.ownerships.all() if o.is_active),
                None
            )

            if not ownership:
                continue

            # Avoid duplicate creation per flat (extra safety)
            if ShareCertificate.objects.filter(
                society=society,
                flat=flat
            ).exists():
                continue

            ShareCertificate.objects.create(
                society=society,
                flat=flat,
                share_count=share_count_per_flat,
                share_value=share_value,
                status="DRAFT"
            )

            created_count += 1

    return Response({
        "message": "Share certificates generated successfully",
        "created": created_count,
        "status": "DRAFT"
    })

from django.utils import timezone
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from society.models import (
    Society,
    FlatOwnership,
    ShareCertificate,
    Committee,
)
from statutory.services import generate_share_certificate_artifact


@api_view(["POST"])
def issue_share_certificates(request):

    society_id = request.data.get("society_id")

    if not society_id:
        return Response({"error": "society_id required"}, status=400)

    society = get_object_or_404(Society, id=society_id)

    # ----------------------------
    # LOCK CHECK (FINAL)
    # ----------------------------
    total = ShareCertificate.objects.filter(society=society).count()

    issued = ShareCertificate.objects.filter(
        society=society,
        status="ISSUED"
    ).count()

    if total > 0 and issued == total:
        return Response(
            {"error": "Share certificates already issued. Step locked."},
            status=403
        )

    # ----------------------------
    # PREREQUISITE CHECK
    # ----------------------------
    has_structure = society.flats.exists()

    has_ownership = FlatOwnership.objects.filter(
        flat__society=society,
        is_active=True
    ).exists()

    has_committee = Committee.objects.filter(
        society=society,
        is_active=True
    ).exists()

    if not (has_structure and has_ownership and has_committee):
        return Response(
            {"error": "Step locked. Complete prior steps."},
            status=403
        )

    # ----------------------------
    # FETCH DRAFT CERTIFICATES
    # ----------------------------
    certificates = ShareCertificate.objects.filter(
        society=society,
        status="DRAFT"
    ).select_related("flat")

    if not certificates.exists():
        return Response({
            "message": "No draft certificates to issue",
            "status": "EMPTY"
        })

    # ----------------------------
    # ALLOCATION START
    # ----------------------------
    counter = 1
    share_start = 1
    issued_count = 0

    with transaction.atomic():

        for cert in certificates:

            flat = cert.flat

            ownership = FlatOwnership.objects.filter(
                flat=flat,
                is_active=True
            ).prefetch_related("owners__person").first()

            if not ownership:
                continue

            owners = ownership.owners.all()

            # ----------------------------
            # SHARE RANGE
            # ----------------------------
            share_end = share_start + cert.share_count - 1

            # ----------------------------
            # CERTIFICATE NUMBER
            # ----------------------------
            certificate_number = str(counter)

            # ----------------------------
            # GENERATE DOCUMENT
            # ----------------------------
            document = generate_share_certificate_artifact(
                society=society,
                flat=flat,
                owners=owners,
                certificate_number=certificate_number,
                share_count=cert.share_count,
                share_value=cert.share_value,
                share_number_from=share_start,
                share_number_to=share_end,
            )

            # ----------------------------
            # UPDATE CERTIFICATE
            # ----------------------------
            cert.certificate_number = certificate_number
            cert.share_number_from = share_start
            cert.share_number_to = share_end
            cert.document = document
            cert.status = "ISSUED"
            cert.issued_on = timezone.now().date()

            cert.save()

            # ----------------------------
            # INCREMENT
            # ----------------------------
            share_start = share_end + 1
            counter += 1
            issued_count += 1

    return Response({
        "message": "Share certificates issued successfully",
        "issued": issued_count,
        "status": "ISSUED"
    })