from datetime import date
from django.utils import timezone
import time
from statutory.models import (
    SocietyLegalProgress,
    SocietyLegalDocument,
    StatutoryAuditLog,
)

# --------------------------------------------------
# NEXT LEGAL STEP
# --------------------------------------------------

def get_next_legal_step(society):
    return (
        SocietyLegalProgress.objects
        .filter(
            society=society,
            status__in=["PENDING", "IN_PROGRESS"]
        )
        .select_related("legal_stage")
        .order_by("legal_stage__sequence_order")
        .first()
    )


# --------------------------------------------------
# RISK COMPUTATION
# --------------------------------------------------

def compute_risk(progress):
    if progress.status == "COMPLETED" or not progress.started_on:
        return "GREEN"

    days_elapsed = (timezone.now().date() - progress.started_on).days
    stage = progress.legal_stage

    if stage.red_after_days and days_elapsed >= stage.red_after_days:
        return "RED"
    if stage.amber_after_days and days_elapsed >= stage.amber_after_days:
        return "AMBER"

    return "GREEN"


# --------------------------------------------------
# AUDIT LOGGING
# --------------------------------------------------

def log_audit_event(
    *,
    society,
    action,
    description,
    legal_stage=None,   # 👈 optional
    user=None,
    source="API",
):

    StatutoryAuditLog.objects.create(
        society=society,
        legal_stage=legal_stage,
        action=action,
        description=description,
        performed_by=user,
        source=source,
    )


# --------------------------------------------------
# STEP COMPLETION (WORKFLOW ONLY)
# --------------------------------------------------

def complete_current_step(society):
    """
    Completes the current legal step and activates the next one.
    Returns: (completed_step, next_step)
    """

    progress = get_next_legal_step(society)

    if not progress:
        return None, None

    # Complete current
    progress.status = "COMPLETED"
    progress.completed_on = date.today()
    progress.save()

    log_audit_event(
        society=society,
        legal_stage=progress.legal_stage,
        action="STEP_COMPLETED",
        description=f"Legal stage '{progress.legal_stage.name}' completed",
    )

    # Start next
    next_step = (
        SocietyLegalProgress.objects
        .filter(
            society=society,
            legal_stage__sequence_order__gt=progress.legal_stage.sequence_order,
            status="PENDING",
        )
        .select_related("legal_stage")
        .order_by("legal_stage__sequence_order")
        .first()
    )

    if next_step:
        next_step.status = "IN_PROGRESS"
        next_step.started_on = date.today()
        next_step.save()

        log_audit_event(
            society=society,
            legal_stage=next_step.legal_stage,
            action="STEP_STARTED",
            description=f"Legal stage '{next_step.legal_stage.name}' started",
        )

    return progress, next_step


# --------------------------------------------------
# FINAL SOCIETY COMPLETION (DOCUMENT-GATED)
# --------------------------------------------------

def finalize_society_if_allowed(society):
    """
    Society can be finalized ONLY if:
    1. All legal stages are completed
    2. All mandatory documents are uploaded
    """

    # Check unfinished steps
    if SocietyLegalProgress.objects.filter(
        society=society
    ).exclude(status="COMPLETED").exists():
        return False, "Pending legal stages exist"

    # Check mandatory documents
    if SocietyLegalDocument.objects.filter(
        society=society,
        template__is_mandatory=True
    ).exclude(status="Uploaded").exists():
        return False, "Mandatory legal documents missing"

    society.legal_status = "LEGALLY_COMPLETE"
    society.save(update_fields=["legal_status"])

    return True, None

# --------------------------------------------------
# SHARE CERTIFICATE GENERATION PIPELINE
# --------------------------------------------------

def build_share_certificate_context(
    *,
    society,
    flat,
    owners,
    certificate_number,
    share_count,
    share_value,
):
    """
    Production-grade context builder for share certificate.
    Supports:
    - Flat-based ownership
    - Multiple owners
    - Legal traceability
    """

    return {
        "society": {
            "name": society.name,
            "registration_number": society.registration_no,
            "address": society.address,
        },
        "certificate": {
            "certificate_number": certificate_number,
            "issued_on": timezone.now().date(),
            "share_count": share_count,
            "share_value": share_value,
        },
        "flat": {
            "flat_number": flat.flat_number,
        },
        "owners": [
            {
                "name": owner.person.full_name
                if owner.person else owner.legal_entity_name
            }
            for owner in owners
        ],
    }


from django.template.loader import render_to_string
def render_share_certificate_html(
    *,
    society,
    flat,
    owners,
    certificate_number,
    share_count,
    share_value,
):
    context = build_share_certificate_context(
        society=society,
        flat=flat,
        owners=owners,
        certificate_number=certificate_number,
        share_count=share_count,
        share_value=share_value,
    )

    return render_to_string(
        "documents/share_certificate.html",
        context,
    )


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os
import time

def generate_share_certificate_pdf(
    *,
    society,
    flat,
    owners,
    certificate_number,
    share_count,
    share_value,
    share_number_from,
    share_number_to,
):
    """
    Production-grade PDF generator.
    Flat-based, multi-owner aware.
    """

    output_dir = os.path.join(
        settings.MEDIA_ROOT,
        "generated",
        "share_certificates",
        str(society.id),
    )
    os.makedirs(output_dir, exist_ok=True)

    safe_certificate_number = certificate_number.replace("/", "_")
    filename = f"{safe_certificate_number}_{int(time.time())}.pdf"
    
    print("FILENAME:", filename)

    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 80

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "SHARE CERTIFICATE")

    y -= 40
    c.setFont("Helvetica", 12)

    c.drawString(80, y, f"Society: {society.name}")
    y -= 20

    c.drawString(80, y, f"Flat: {flat.flat_number}")
    y -= 20

    owner_names = ", ".join([
        o.person.full_name if o.person else o.legal_entity_name
        for o in owners
    ])
    c.drawString(80, y, f"Owners: {owner_names}")
    y -= 20

    c.drawString(80, y, f"Share Numbers: {share_number_from} to {share_number_to}")
    y -= 20

    c.drawString(80, y, f"Share Value: ₹{share_value}")
    y -= 20

    c.drawString(80, y, f"Certificate No: {certificate_number}")
    y -= 20

    c.drawString(80, y, f"Issued On: {timezone.now().date()}")

    c.showPage()
    c.save()

    return file_path


from statutory.models import SocietyLegalDocument, LegalArtifactTemplate

def attach_share_certificate_document(
    *,
    society,
    file_path,
    flat,
    certificate_number,
):
    """
    Attaches generated certificate to legal document system.
    """

    template = LegalArtifactTemplate.objects.filter(
        artifact_code="SHARE_CERTIFICATE"
    ).first()

    if not template:
        raise ValueError("SHARE_CERTIFICATE template not configured")

    relative_path = file_path.replace(
        str(settings.MEDIA_ROOT) + "/", ""
    )

    document = SocietyLegalDocument.objects.filter(
        society=society,
        template=template,
    ).first()

    if not document:
        document = SocietyLegalDocument.objects.create(
            society=society,
            template=template,
            file=relative_path,
            status="GENERATED",
            uploaded_at=timezone.now(),
        )
    else:
        # update existing document instead of creating new
        document.file = relative_path
        document.status = "GENERATED"
        document.uploaded_at = timezone.now()
        document.save(update_fields=["file", "status", "uploaded_at"])

    return document

def generate_share_certificate_artifact(
    *,
    society,
    flat,
    owners,
    certificate_number,
    share_count,
    share_value,
    share_number_from,
    share_number_to,
):
    """
    Master orchestration function.
    Generates:
    - PDF
    - Legal document
    Returns document instance
    """

    pdf_path = generate_share_certificate_pdf(
        society=society,
        flat=flat,
        owners=owners,
        certificate_number=certificate_number,
        share_count=share_count,
        share_value=share_value,
        share_number_from=share_number_from,
        share_number_to=share_number_to,
    )

    document = attach_share_certificate_document(
        society=society,
        file_path=pdf_path,
        flat=flat,
        certificate_number=certificate_number,
    )

    return document


from statutory.models import ShareOwnership


def transfer_shares(*, society, from_member, to_member, shares=1):
    """
    Transfers shares safely.
    Preserves full ownership history.
    """

    current = ShareOwnership.objects.filter(
        society=society,
        member=from_member,
        is_active=True,
    ).first()

    if not current:
        raise ValueError("No active shares to transfer")

    # 🔒 Close old ownership
    current.is_active = False
    current.relinquished_on = timezone.now().date()
    current.save()

    # 🔴 Supersede old certificate
    supersede_existing_share_certificate(
        society=society,
        reason="Share transfer executed",
    )

    # 🆕 Create new ownership
    new_ownership = ShareOwnership.objects.create(
        society=society,
        member=to_member,
        shares=shares,
        acquired_on=timezone.now().date(),
        is_active=True,
    )

    # 🆕 Regenerate certificate
    regenerate_share_certificate_after_transfer(
        society=society,
        new_owner=to_member,
    )

    # 🧾 Audit
    log_audit_event(
        society=society,
        action="SHARE_TRANSFERRED",
        description=f"Shares transferred from {from_member} to {to_member}",
    )

    return new_ownership


    # 🆕 Create new ownership
    new_ownership = ShareOwnership.objects.create(
        society=society,
        member=to_member,
        shares=shares,
        acquired_on=timezone.now().date(),
        is_active=True,
    )

    # 🧾 Audit
    log_audit_event(
        society=society,
        action="SHARE_TRANSFERRED",
        description=f"Shares transferred from {from_member} to {to_member}",
    )

    return new_ownership
from statutory.models import SocietyLegalDocument


def supersede_existing_share_certificate(*, society, reason=None):
    """
    Marks the currently active share certificate (if any) as SUPERSEDED.
    """
    active_doc = (
        SocietyLegalDocument.objects
        .filter(
            society=society,
            template__artifact_type="SHARE_CERTIFICATE",
            status__in=["GENERATED", "UPLOADED", "APPROVED"],
        )
        .order_by("-uploaded_at")
        .first()
    )

    if not active_doc:
        return None  # Nothing to supersede

    active_doc.status = "SUPERSEDED"
    active_doc.save(update_fields=["status"])

    return active_doc
def regenerate_share_certificate_after_transfer(*, society, new_owner):
    """
    Generates and attaches a fresh share certificate
    after a share transfer.
    """

    # TODO: Rebuild using new flat-based engine
    doc = None
    status = "REQUIRES_REGENERATION_PIPELINE"
    
    return doc, status
