import uuid
from django.db import models


class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    scope = models.CharField(
        max_length=50,
        choices=[
            ("SYSTEM", "System"),
            ("SOCIETY", "Society"),
            ("BUILDING", "Building"),
            ("UNIT", "Unit"),
        ]
    )

    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code", "-version"]


class PolicyRule(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="rules")
    effect = models.CharField(max_length=10, choices=[("ALLOW", "Allow"), ("DENY", "Deny")])
    condition = models.JSONField()
    priority = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["priority"]


class PolicyAssignment(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="assignments")
    role = models.CharField(max_length=50, null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True)
    society_id = models.UUIDField(null=True, blank=True)


class PolicyDecisionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_code = models.CharField(max_length=100)
    policy_version = models.PositiveIntegerField()
    actor_id = models.UUIDField()
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=255)
    decision = models.CharField(max_length=10, choices=[("ALLOW", "Allow"), ("DENY", "Deny")])
    reason = models.TextField()
    decision_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
