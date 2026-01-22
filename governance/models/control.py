from django.db import models

class GovernanceControl(models.Model):
    MODE_CHOICES = [
        ("OBSERVE_ONLY", "Observe Only"),
        ("PROGRESSIVE", "Progressive"),
        ("STRICT", "Strict"),
    ]

    enforcement_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default="OBSERVE_ONLY"
    )

    policy_engine_enabled = models.BooleanField(default=True)
    simulation_enabled = models.BooleanField(default=True)
    rollback_enabled = models.BooleanField(default=True)
    audit_enabled = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Governance Control"
