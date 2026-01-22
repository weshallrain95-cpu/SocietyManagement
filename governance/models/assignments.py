# governance/models/assignments.py
from django.db import models
from .policy import Policy
import uuid

class PolicyAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="assignments")
    role = models.CharField(max_length=50, null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True)
    society_id = models.UUIDField(null=True, blank=True)

    class Meta:
        unique_together = ("policy", "role", "user_id", "society_id")
