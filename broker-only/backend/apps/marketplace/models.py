from django.conf import settings
from django.contrib.gis.db import models as gis
from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import BaseModel


class Enquiry(BaseModel):
    """A customer's requirement broadcast to eligible brokers (MKT-03..09)."""

    class State(models.TextChoices):
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        FULFILLED = "fulfilled"
        CANCELLED = "cancelled"
        EXPIRED = "expired"

    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enquiries")
    txn_type = models.CharField(max_length=12)
    property_types = ArrayField(models.CharField(max_length=20), default=list, blank=True)
    bhk_min = models.DecimalField(max_digits=3, decimal_places=1)
    bhk_max = models.DecimalField(max_digits=3, decimal_places=1)
    budget_min = models.PositiveBigIntegerField(null=True, blank=True)
    budget_max = models.PositiveBigIntegerField()
    center = gis.PointField(geography=True)
    radius_m = models.PositiveIntegerField(default=3000)
    area_label = models.CharField(max_length=120, blank=True)
    must_haves = models.JSONField(default=dict, blank=True)
    house_rule_needs = models.JSONField(default=dict, blank=True)
    max_station_distance_m = models.PositiveIntegerField(null=True, blank=True)
    move_in_by = models.DateField(null=True, blank=True)
    urgency = models.CharField(max_length=8, default="normal")
    occupants = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=500, blank=True)
    summary_text = models.CharField(max_length=300)
    state = models.CharField(max_length=12, choices=State.choices, default=State.OPEN)
    expires_at = models.DateTimeField()
    n_recipients = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["state", "created_at"])]


class EnquiryDelivery(BaseModel):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="deliveries")
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+")
    channel = models.CharField(max_length=10)
    match_count = models.PositiveIntegerField(default=0)
    seen_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["enquiry", "org"], name="one_delivery_per_org")]


class Proposal(BaseModel):
    class State(models.TextChoices):
        SENT = "sent"
        ACCEPTED = "accepted"
        DECLINED = "declined"
        EXPIRED = "expired"
        WITHDRAWN = "withdrawn"

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name="proposals")
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="proposals")
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    message = models.CharField(max_length=500, blank=True)
    brokerage_terms = models.CharField(max_length=200)
    match_count = models.PositiveIntegerField(default=0)
    earliest_slot = models.DateTimeField(null=True, blank=True)
    teaser_society_ids = ArrayField(models.UUIDField(), default=list, blank=True)
    response_s = models.PositiveIntegerField()
    promoted = models.BooleanField(default=False)
    state = models.CharField(max_length=10, choices=State.choices, default=State.SENT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["enquiry", "org"], name="one_proposal_per_org")]


class SupplyCell(models.Model):
    """Aggregated, anonymous supply per H3 cell for the customer map (Data Model §8)."""

    h3_index = models.CharField(max_length=16)
    resolution = models.PositiveSmallIntegerField()
    txn_type = models.CharField(max_length=12)
    bhk_bucket = models.CharField(max_length=4)
    units_available = models.PositiveIntegerField()
    price_p25 = models.PositiveBigIntegerField(null=True)
    price_p50 = models.PositiveBigIntegerField(null=True)
    price_p75 = models.PositiveBigIntegerField(null=True)
    brokers_serving = models.PositiveIntegerField(default=0)
    lat = models.FloatField()
    lng = models.FloatField()
    refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["h3_index", "txn_type", "bhk_bucket"], name="uniq_cell")]
        indexes = [models.Index(fields=["resolution", "txn_type"])]
