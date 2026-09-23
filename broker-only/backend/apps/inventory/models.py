"""Broker-private inventory. Every table here is protected by Postgres row-level security."""

from django.conf import settings
from django.db import models

from common import crypto
from common.models import BaseModel


class Listing(BaseModel):
    """One broker's private claim on a unit (INV-01/02). Many brokers may list the same unit."""

    class Origin(models.TextChoices):
        MANUAL = "manual"
        UPLOAD = "upload"
        OWNER_INVITE = "owner_invite"
        BUILDER = "builder"

    class Visibility(models.TextChoices):
        PRIVATE = "private"
        PUBLISH_CARD = "publish_card"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="listings", db_column="broker_org_id")
    unit = models.ForeignKey("masterdata.Unit", on_delete=models.PROTECT, related_name="listings")
    txn_type = models.CharField(max_length=12)
    asking_rent = models.PositiveIntegerField(null=True, blank=True, help_text="INR per month")
    asking_price = models.PositiveBigIntegerField(null=True, blank=True, help_text="INR")
    deposit = models.PositiveIntegerField(null=True, blank=True)
    maintenance = models.PositiveIntegerField(null=True, blank=True)
    negotiable = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    brokerage_terms = models.CharField(max_length=200, blank=True)
    owner_name = models.CharField(max_length=120, blank=True)
    owner_phone_enc = models.BinaryField(null=True, blank=True)
    origin = models.CharField(max_length=14, choices=Origin.choices, default=Origin.MANUAL)
    visibility = models.CharField(max_length=14, choices=Visibility.choices, default=Visibility.PRIVATE)
    withdrawn_by_owner = models.BooleanField(default=False)
    last_confirmed_at = models.DateTimeField()
    private_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["org", "unit", "txn_type"], condition=models.Q(archived_at__isnull=True), name="one_live_listing_per_org_unit_txn"
            )
        ]
        indexes = [models.Index(fields=["org", "txn_type", "archived_at"])]

    @property
    def owner_phone(self):
        return crypto.decrypt(self.owner_phone_enc)

    @property
    def price(self):
        return self.asking_rent if self.txn_type == "RENT" else self.asking_price


class KeyCustody(BaseModel):
    class Holder(models.TextChoices):
        OWNER = "owner"
        OFFICE = "office"
        STAFF = "staff"
        SOCIETY_OFFICE = "society_office"
        LOCKBOX = "lockbox"
        NEIGHBOUR = "neighbour"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="keys")
    holder_type = models.CharField(max_length=16, choices=Holder.choices)
    holder_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    instructions_enc = models.BinaryField(null=True, blank=True)
    from_ts = models.DateTimeField(auto_now_add=True)
    to_ts = models.DateTimeField(null=True, blank=True)
    needs_handover = models.BooleanField(default=False)

    @property
    def instructions(self):
        return crypto.decrypt(self.instructions_enc)


class UploadBatch(BaseModel):
    class State(models.TextChoices):
        PARSING = "parsing"
        AWAITING_REVIEW = "awaiting_review"
        COMMITTED = "committed"
        FAILED = "failed"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    filename = models.CharField(max_length=200)
    micro_market = models.ForeignKey("masterdata.MicroMarket", null=True, on_delete=models.SET_NULL, related_name="+")
    default_txn_type = models.CharField(max_length=12, default="RENT")
    column_mapping = models.JSONField(default=dict)
    state = models.CharField(max_length=16, choices=State.choices, default=State.PARSING)
    counts = models.JSONField(default=dict)
    error = models.TextField(blank=True)


class UploadRow(BaseModel):
    class Resolution(models.TextChoices):
        AUTO = "auto"
        NEEDS_CONFIRMATION = "needs_confirmation"
        BROKER_CONFIRMED = "broker_confirmed"
        PROVISIONAL = "provisional"
        ERROR = "error"
        SKIPPED = "skipped"
        COMMITTED = "committed"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    batch = models.ForeignKey(UploadBatch, on_delete=models.CASCADE, related_name="rows")
    row_no = models.PositiveIntegerField()
    raw = models.JSONField()
    parsed = models.JSONField(default=dict)
    candidates = models.JSONField(default=list)
    society = models.ForeignKey("masterdata.Society", null=True, on_delete=models.SET_NULL, related_name="+")
    resolution = models.CharField(max_length=20, choices=Resolution.choices)
    errors = models.JSONField(default=list)
    listing = models.ForeignKey(Listing, null=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        ordering = ["row_no"]


class SavedColumnMapping(BaseModel):
    """INV-03: the wizard remembers each broker's Excel headers."""

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    header_signature = models.CharField(max_length=64)
    mapping = models.JSONField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["org", "header_signature"], name="uniq_mapping")]
