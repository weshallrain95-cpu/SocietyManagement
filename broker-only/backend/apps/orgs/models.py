from django.conf import settings
from django.contrib.gis.db import models as gis
from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import BaseModel

TXN_TYPES = [("RENT", "Rent"), ("SALE_NEW", "Sale – new"), ("SALE_RESALE", "Sale – resale")]


class BrokerOrg(BaseModel):
    """An agency. A solo broker is an org of one."""

    class Verification(models.TextChoices):
        PENDING = "pending"
        VERIFIED = "verified"
        REJECTED = "rejected"
        SUSPENDED = "suspended"

    name = models.CharField(max_length=160)
    office_location = gis.PointField(geography=True, null=True, blank=True)
    office_address = models.CharField(max_length=300, blank=True)
    rera_agent_no = models.CharField(max_length=30, blank=True)
    rera_verified_at = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(max_length=10, choices=Verification.choices, default=Verification.PENDING)
    verification_note = models.CharField(max_length=300, blank=True)
    txn_types = ArrayField(models.CharField(max_length=12, choices=TXN_TYPES), default=list)
    languages = ArrayField(models.CharField(max_length=5), default=list, blank=True)
    plan_code = models.CharField(max_length=20, default="free")
    rating_bayes = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    rating_count = models.PositiveIntegerField(default=0)
    median_response_s = models.PositiveIntegerField(null=True, blank=True)
    listing_accuracy = models.DecimalField(max_digits=4, decimal_places=3, default=1)
    closures = models.PositiveIntegerField(default=0)
    # Online for customer enquiries from sign-up; "Go offline" is the broker's opt-out (MKT-11).
    accepting_enquiries = models.BooleanField(default=True)

    @property
    def is_verified(self):
        return self.verification_status == self.Verification.VERIFIED

    def __str__(self):
        return self.name


class Membership(BaseModel):
    class Role(models.TextChoices):
        PRINCIPAL = "broker_principal"
        MANAGER = "broker_manager"
        STAFF = "broker_staff"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    org = models.ForeignKey(BrokerOrg, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=Role.choices)
    active = models.BooleanField(default=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "org"], condition=models.Q(active=True), name="one_active_membership")]

    @property
    def can_manage(self):
        return self.role in (self.Role.PRINCIPAL, self.Role.MANAGER)


class ServiceArea(BaseModel):
    org = models.ForeignKey(BrokerOrg, on_delete=models.CASCADE, related_name="service_areas")
    area = gis.MultiPolygonField(srid=4326)
    label = models.CharField(max_length=120, blank=True)
    locality = models.ForeignKey("masterdata.Locality", null=True, blank=True, on_delete=models.SET_NULL)
    txn_types = ArrayField(models.CharField(max_length=12, choices=TXN_TYPES), default=list)
