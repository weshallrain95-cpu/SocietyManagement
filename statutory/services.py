from datetime import date
from django.utils import timezone
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
def build_share_certificate_context(*, society, member):
    """
    Phase-1 Share Certificate context.
    Ownership history has a single row.
    """

    return {
        "society": {
            "name": society.name,
            "registration_number": society.registration_no,
            "address": society.address,
        },
        "certificate": {
            "issued_on": timezone.now().date(),
            "certificate_number": f"SC-{society.id}-{member.id}",
        },
        "ownership_history": [
            {
                "sr_no": 1,
                "member_name": member.get_full_name(),
                "from_date": timezone.now().date(),
                "to_date": None,
            }
        ],
    }
from django.template.loader import render_to_string


def render_share_certificate_html(*, society, member):
    context = build_share_certificate_context(
        society=society,
        member=member,
    )

    return render_to_string(
        "documents/share_certificate.html",
        context,
    )
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings
import os
from django.utils import timezone


def generate_share_certificate_pdf(*, society, member):
    output_dir = os.path.join(
        settings.MEDIA_ROOT,
        "generated",
        "share_certificates",
    )
    os.makedirs(output_dir, exist_ok=True)

    filename = f"share_certificate_soc_{society.id}_mem_{member.id}.pdf"
    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 80

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y, "SHARE CERTIFICATE")

    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(80, y, f"Society: {society.name}")

    y -= 25
    c.drawString(80, y, f"Member: {member.get_full_name()}")

    y -= 25
    c.drawString(80, y, f"Issued on: {timezone.now().date()}")

    y -= 40
    c.drawString(80, y, "This certifies that the above member holds shares")

    c.showPage()
    c.save()

    return file_path
from statutory.models import SocietyLegalDocument, LegalArtifactTemplate
from django.utils import timezone


def generate_and_attach_share_certificate(*, society, member):
    """
    Generates ONE share certificate per society.
    Idempotent and legally safe.
    """

    # 🔒 Step 1: Block duplicates
    existing = SocietyLegalDocument.objects.filter(
        society=society,
        template__artifact_type="SHARE_CERTIFICATE",
        status__in=["Generated", "Uploaded"],
    ).first()

    if existing:
        return existing, "ALREADY_EXISTS"

    # 📄 Step 2: Fetch template
    template = LegalArtifactTemplate.objects.get(
        artifact_type="SHARE_CERTIFICATE"
    )

    # 🧠 Step 3: Generate PDF
    pdf_path = generate_share_certificate_pdf(
        society=society,
        member=member,
    )

    # 📎 Step 4: Attach document
    document = SocietyLegalDocument.objects.create(
        society=society,
        template=template,
        file=str(pdf_path).replace(str(settings.MEDIA_ROOT) + "/", ""),
        status="Generated",
        uploaded_at=timezone.now(),
    )

    return document, "CREATED"
from statutory.models import ShareOwnership
from django.utils import timezone


def transfer_shares(*, society, from_member, to_member, shares=1):
    """
    Transfers shares safely.
    Preserves full ownership history.
    """

    # 🔍 Find active ownership
    current = ShareOwnership.objects.filter(
        society=society,
        member=from_member,
        is_active=True,
    ).first()

    if not current:
        raise ValueError("No active shares to transfer")

    # 🔒 Close current ownership
    current.is_active = False
    current.relinquished_on = timezone.now().date()
    current.save()


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
from django.utils import timezone


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

    doc, status = generate_and_attach_share_certificate(
        society=society,
        member=new_owner,
        reason="Regenerated after share transfer",
    )

    return doc, status
