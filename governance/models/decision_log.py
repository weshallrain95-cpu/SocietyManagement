from django.db import models
import uuid

class PolicyDecisionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_code = models.CharField(max_length=100)
    policy_version = models.PositiveIntegerField()
    actor_id = models.UUIDField()
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=255)
    decision = models.CharField(max_length=10)
    reason = models.TextField()
    decision_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
