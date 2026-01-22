# governance/models/rules.py
from django.db import models
from .policy import Policy
import uuid

class PolicyRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    EFFECT_CHOICES = [
        ("ALLOW", "ALLOW"),
        ("DENY", "DENY"),
        ("SOFT_DENY", "SOFT_DENY"),
        ("OBSERVE", "OBSERVE"),
    ]

    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="rules")
    effect = models.CharField(max_length=10, choices=EFFECT_CHOICES)
    condition = models.JSONField()
    priority = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return f"{self.policy.code}:{self.effect}:{self.priority}"
