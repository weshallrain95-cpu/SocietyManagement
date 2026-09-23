from django.db import models

from .ids import uuid7


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DomainEvent(models.Model):
    """Transactional outbox. Written in the same transaction as the state change it describes."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80, db_index=True)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["processed_at", "id"], name="outbox_pending_idx")]


class ShareLink(BaseModel):
    """A tokenised link for people without the app (owners, offline customers).

    Only sha256(token) is stored; the raw token exists once, in the message we send.
    """

    class Purpose(models.TextChoices):
        STATUS_CONFIRMATION = "status_confirmation"
        VISIT_PLAN = "visit_plan"
        SHORTLIST = "shortlist"
        REVIEW = "review"
        CONSENT = "consent"
        VISIT_NOTICE = "visit_notice"

    purpose = models.CharField(max_length=32, choices=Purpose.choices)
    token_hash = models.CharField(max_length=64, unique=True)
    target_type = models.CharField(max_length=40)
    target_id = models.UUIDField()
    recipient_phone_hash = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)
    uses = models.PositiveIntegerField(default=0)
    revoked_at = models.DateTimeField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [models.Index(fields=["target_type", "target_id"])]


class Notification(BaseModel):
    """Every outbound message (in-app, push, WhatsApp, SMS) with its delivery outcome."""

    user = models.ForeignKey("identity.User", null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    phone_hash = models.CharField(max_length=64, blank=True, help_text="For people without an account")
    org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    template = models.CharField(max_length=60)
    channel = models.CharField(max_length=12, default="inapp")
    payload = models.JSONField(default=dict)
    state = models.CharField(max_length=12, default="queued")
    read_at = models.DateTimeField(null=True, blank=True)
    provider_msg_id = models.CharField(max_length=80, blank=True)


class ReviewQueueItem(BaseModel):
    """Admin work queue: provisional societies, disputes, status conflicts, reported enquiries/reviews."""

    kind = models.CharField(max_length=40, db_index=True)
    ref_type = models.CharField(max_length=60)
    ref_id = models.CharField(max_length=64)
    summary = models.CharField(max_length=300)
    data = models.JSONField(default=dict, blank=True)
    state = models.CharField(max_length=12, default="open", db_index=True)
    resolved_by = models.ForeignKey("identity.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution = models.CharField(max_length=300, blank=True)
