from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.models import BaseModel


class Interaction(BaseModel):
    """A verified relationship that makes reviews possible (REV-01)."""

    class Kind(models.TextChoices):
        VISIT_COMPLETED = "visit_completed"
        DEAL_CLOSED = "deal_closed"
        OWNER_REPRESENTATION = "owner_representation"

    kind = models.CharField(max_length=24, choices=Kind.choices)
    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+")
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    customer_phone_hash = models.CharField(max_length=64, blank=True, help_text="Offline customers (OFF-08)")
    owner_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    ref_type = models.CharField(max_length=40)
    ref_id = models.UUIDField()
    occurred_at = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=["kind", "ref_type", "ref_id"], name="one_interaction_per_ref")]


class Review(BaseModel):
    class Direction(models.TextChoices):
        C2B = "C2B"
        B2C = "B2C"
        O2B = "O2B"
        B2O = "B2O"
        C2U = "C2U"

    interaction = models.ForeignKey(Interaction, on_delete=models.CASCADE, related_name="reviews")
    direction = models.CharField(max_length=3, choices=Direction.choices)
    reviewer_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    reviewer_label = models.CharField(max_length=60, blank=True)
    org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.CASCADE, related_name="reviews")
    reviewee_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="+")
    stars = models.PositiveSmallIntegerField()
    tags = ArrayField(models.CharField(max_length=30), default=list, blank=True)
    text = models.CharField(max_length=1000, blank=True)
    moderation_state = models.CharField(max_length=10, default="published")
    reply_text = models.CharField(max_length=1000, blank=True)
    verified_offline = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["interaction", "direction"], name="one_review_per_interaction_direction"),
            models.CheckConstraint(condition=models.Q(stars__gte=1, stars__lte=5), name="stars_1_5"),
        ]
