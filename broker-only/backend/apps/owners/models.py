"""Owners module (PRD OWN-01..06, founder decisions D13/D14).

- An owner registers their flat with a proof document. Nobody checks it: it deters false claims,
  it doesn't block (D14).
- Photos/videos belong to the flat (shared, D15): at most 5 photos and 1 video live. The owner and the
  brokers holding the flat may upload; customers never. Nothing goes live until the owner approves it
  (the owner's own uploads are live at once). Live media is shown to every broker holding the flat and,
  while the switch is on, on customer links.
- An owner hands a flat to a broker only after ticking "Allow this broker to handle my property".
- An owner can untick any broker (invited or self-added): that broker loses the flat and cannot
  re-add it until the owner allows them again. The owner's decision is final.
"""

from django.conf import settings
from django.db import models

from common.models import BaseModel


class UnitMedia(BaseModel):
    class Kind(models.TextChoices):
        PHOTO = "photo"
        VIDEO = "video"
        DOCUMENT = "document"  # proof of ownership: private to the owner (and ops in a dispute)

    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="media")
    claim = models.ForeignKey("masterdata.OwnershipClaim", null=True, blank=True, on_delete=models.SET_NULL, related_name="media")

    class State(models.TextChoices):
        PENDING = "pending"  # uploaded by a broker, waiting for the owner
        LIVE = "live"
        REJECTED = "rejected"

    kind = models.CharField(max_length=10, choices=Kind.choices)
    state = models.CharField(max_length=10, choices=State.choices, default=State.LIVE)
    uploaded_by_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to="units/%Y/%m/")
    thumb = models.FileField(upload_to="units/%Y/%m/", blank=True)
    content_type = models.CharField(max_length=60)
    size_bytes = models.PositiveBigIntegerField()
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    caption = models.CharField(max_length=120, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["unit", "kind"])]


class OwnerInvite(BaseModel):
    """Owner → broker. Exists only once the owner ticked "Allow this broker to handle my property"."""

    class State(models.TextChoices):
        PENDING = "pending"
        ACCEPTED = "accepted"
        DECLINED = "declined"
        CANCELLED = "cancelled"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="+")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    txn_type = models.CharField(max_length=12, default="RENT")
    terms = models.JSONField(default=dict, blank=True)
    allowed_at = models.DateTimeField(help_text="When the owner ticked 'Allow this broker to handle my property'")
    state = models.CharField(max_length=10, choices=State.choices, default=State.PENDING)
    listing = models.ForeignKey("inventory.Listing", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["org", "unit"], condition=models.Q(state="pending"), name="one_pending_invite_per_org_unit")
        ]


class OwnerWithdrawal(BaseModel):
    """The owner unticked a broker: while active, that firm cannot hold or re-add this flat."""

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="+")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    reason = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)
    reinstated_at = models.DateTimeField(null=True, blank=True)
    ask_note = models.CharField(max_length=300, blank=True, help_text="The broker's request to be added back")
    asked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["org", "unit"], condition=models.Q(active=True), name="one_active_withdrawal")]
