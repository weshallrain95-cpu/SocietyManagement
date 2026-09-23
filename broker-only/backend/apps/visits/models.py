from django.conf import settings
from django.contrib.gis.db import models as gis
from django.db import models

from common.models import BaseModel


class VisitPlan(BaseModel):
    class State(models.TextChoices):
        DRAFT = "draft"
        SHARED = "shared"
        CUSTOMER_CONFIRMED = "customer_confirmed"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    class Mode(models.TextChoices):
        DRIVE = "drive"
        TWO_WHEELER = "two_wheeler"
        WALK = "walk"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    customer = models.ForeignKey("crm.Customer", on_delete=models.CASCADE, related_name="visit_plans")
    requirement = models.ForeignKey("crm.Requirement", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    date = models.DateField()
    start_time = models.TimeField()
    start_point = gis.PointField(geography=True, null=True, blank=True)
    travel_mode = models.CharField(max_length=12, choices=Mode.choices, default=Mode.TWO_WHEELER)
    dwell_min = models.PositiveSmallIntegerField(default=15)
    state = models.CharField(max_length=20, choices=State.choices, default=State.DRAFT)
    customer_proposed_slot = models.DateTimeField(null=True, blank=True)
    route_method = models.CharField(max_length=20, blank=True)
    total_travel_min = models.PositiveIntegerField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")


class VisitStop(BaseModel):
    class Outcome(models.TextChoices):
        LIKED = "liked"
        REJECTED = "rejected"
        SHORTLISTED = "shortlisted"
        SECOND_VISIT = "second_visit"
        NO_SHOW = "no_show"
        NOT_ACCESSIBLE = "not_accessible"
        ALREADY_LET = "already_let"

    class OwnerNotice(models.TextChoices):
        NOT_REQUIRED = "not_required"
        SENT = "sent"
        ACKNOWLEDGED = "acknowledged"
        DECLINED = "declined"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    plan = models.ForeignKey(VisitPlan, on_delete=models.CASCADE, related_name="stops")
    seq = models.PositiveSmallIntegerField()
    listing = models.ForeignKey("inventory.Listing", on_delete=models.PROTECT, related_name="+")
    slot_start = models.DateTimeField(null=True, blank=True)
    slot_end = models.DateTimeField(null=True, blank=True)
    assigned_staff = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    staff_ack_at = models.DateTimeField(null=True, blank=True)
    owner_notice = models.CharField(max_length=14, choices=OwnerNotice.choices, default=OwnerNotice.NOT_REQUIRED)
    checkin_at = models.DateTimeField(null=True, blank=True)
    checkout_at = models.DateTimeField(null=True, blank=True)
    checkin_distance_m = models.PositiveIntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=16, choices=Outcome.choices, blank=True)
    reject_reasons = models.JSONField(default=list, blank=True)
    feedback_note = models.CharField(max_length=500, blank=True)
    removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["seq"]


class SyncMutation(models.Model):
    """OFF-10/11: idempotency ledger for mutations queued on an offline device."""

    idempotency_key = models.CharField(max_length=64, primary_key=True)
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    device_id = models.CharField(max_length=64)
    entity = models.CharField(max_length=30)
    payload = models.JSONField()
    client_ts = models.DateTimeField()
    applied_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=10)
    detail = models.JSONField(default=dict)
