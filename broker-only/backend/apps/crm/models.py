"""The broker's customer book (CRM-*, OFF-*). Private to the broker org via RLS."""

from django.conf import settings
from django.contrib.gis.db import models as gis
from django.contrib.postgres.fields import ArrayField
from django.db import models

from common import crypto
from common.models import BaseModel


class Customer(BaseModel):
    class Source(models.TextChoices):
        MARKETPLACE = "marketplace"
        PHONE_CALL = "phone_call"
        WALK_IN = "walk_in"
        REFERRAL = "referral"
        BOARD = "board"
        WHATSAPP_GROUP = "whatsapp_group"
        IMPORT = "import"
        OTHER = "other"

    class Consent(models.TextChoices):
        NONE = "none"
        ATTESTED_VERBAL = "attested_verbal"
        OTP_CONFIRMED = "otp_confirmed"
        LINK_CONFIRMED = "link_confirmed"
        APP = "app"
        WITHDRAWN = "withdrawn"

    class Stage(models.TextChoices):
        NEW = "new"
        CONTACTED = "contacted"
        VISITS_PLANNED = "visits_planned"
        SHORTLISTED = "shortlisted"
        NEGOTIATION = "negotiation"
        WON = "closed_won"
        LOST = "closed_lost"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    phone_hash = models.CharField(max_length=64)
    phone_enc = models.BinaryField()
    name = models.CharField(max_length=120, blank=True)
    source = models.CharField(max_length=16, choices=Source.choices)
    platform_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    consent_state = models.CharField(max_length=16, choices=Consent.choices, default=Consent.NONE)
    consent_evidence = models.JSONField(default=dict, blank=True)
    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.NEW)
    lost_reason = models.CharField(max_length=200, blank=True)
    tags = ArrayField(models.CharField(max_length=30), default=list, blank=True)
    notes = models.TextField(blank=True)
    next_follow_up = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    updates_muted = models.BooleanField(default=False, help_text="The customer turned off this broker's broadcast updates")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["org", "phone_hash"], name="one_customer_per_phone_per_org")]

    @property
    def phone(self):
        return crypto.decrypt(self.phone_enc)

    @property
    def can_message(self) -> bool:
        return self.consent_state in (
            self.Consent.OTP_CONFIRMED,
            self.Consent.LINK_CONFIRMED,
            self.Consent.APP,
            self.Consent.ATTESTED_VERBAL,
        )


class Requirement(BaseModel):
    """What the customer wants. Same shape as a marketplace enquiry (MKT-03)."""

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="requirements")
    enquiry = models.ForeignKey("marketplace.Enquiry", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    txn_type = models.CharField(max_length=12)
    property_types = ArrayField(models.CharField(max_length=20), default=list, blank=True)
    bhk_min = models.DecimalField(max_digits=3, decimal_places=1)
    bhk_max = models.DecimalField(max_digits=3, decimal_places=1)
    budget_min = models.PositiveBigIntegerField(null=True, blank=True)
    budget_max = models.PositiveBigIntegerField()
    search_area = gis.MultiPolygonField(srid=4326, null=True, blank=True)
    localities = models.ManyToManyField("masterdata.Locality", blank=True, related_name="+")
    max_station_distance_m = models.PositiveIntegerField(null=True, blank=True)
    must_haves = models.JSONField(default=dict, blank=True, help_text="attr_key -> required value")
    nice_to_haves = models.JSONField(default=dict, blank=True)
    house_rule_needs = models.JSONField(default=dict, blank=True, help_text='e.g. {"pets": "dog", "nonveg_cooking": true}')
    move_in_by = models.DateField(null=True, blank=True)
    occupants = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)


class CustomerInteraction(BaseModel):
    class Kind(models.TextChoices):
        CALL_IN = "call_in"
        CALL_OUT = "call_out"
        OFFICE_MEETING = "office_meeting"
        WHATSAPP = "whatsapp"
        SMS = "sms"
        LINK_OPENED = "link_opened"
        SHORTLIST_RESPONSE = "shortlist_response"
        VISIT = "visit"
        NOTE = "note"
        SYSTEM = "system"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="interactions")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    occurred_at = models.DateTimeField()
    duration_s = models.PositiveIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=500, blank=True)
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    ref_type = models.CharField(max_length=40, blank=True)
    ref_id = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-occurred_at"]


class Shortlist(BaseModel):
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="shortlists")
    requirement = models.ForeignKey(Requirement, null=True, on_delete=models.SET_NULL, related_name="+")
    title = models.CharField(max_length=120, blank=True)
    shared_at = models.DateTimeField(null=True, blank=True)


class ShortlistItem(BaseModel):
    class Response(models.TextChoices):
        INTERESTED = "interested"
        NOT_FOR_ME = "not_for_me"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    shortlist = models.ForeignKey(Shortlist, on_delete=models.CASCADE, related_name="items")
    listing = models.ForeignKey("inventory.Listing", on_delete=models.CASCADE, related_name="+")
    position = models.PositiveSmallIntegerField(default=0)
    customer_response = models.CharField(max_length=12, choices=Response.choices, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position"]


class Broadcast(BaseModel):
    """One message from a broker to many of their own customers (D16): new flat, price drop, area news.

    The customer list is the broker's asset: only this firm's customers are ever reached, and the
    platform never shares or moves customers between brokers. Delivered in the app (pilot); customers
    not yet on the app are listed so the broker can invite them.
    """

    class Kind(models.TextChoices):
        NEW_FLAT = "new_flat"
        PRICE_DROP = "price_drop"
        NEWS = "news"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    text = models.CharField(max_length=500)
    listing = models.ForeignKey("inventory.Listing", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    locality = models.ForeignKey("masterdata.Locality", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    audience = models.JSONField(default=dict, blank=True)
    recipients_total = models.PositiveIntegerField(default=0)
    delivered_in_app = models.PositiveIntegerField(default=0)
    not_on_app = models.PositiveIntegerField(default=0)
    muted = models.PositiveIntegerField(default=0)
