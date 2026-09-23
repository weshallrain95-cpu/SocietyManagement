from django.db import models


class AuditEvent(models.Model):
    """Append-only, hash-chained audit log (UPDATE/DELETE blocked by a trigger)."""

    seq = models.BigAutoField(primary_key=True)
    at = models.DateTimeField()
    actor_id = models.UUIDField(null=True, blank=True)
    actor_label = models.CharField(max_length=60, blank=True)
    action = models.CharField(max_length=80, db_index=True)
    target_type = models.CharField(max_length=60)
    target_id = models.CharField(max_length=64)
    data = models.JSONField(default=dict)
    prev_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)

    class Meta:
        indexes = [models.Index(fields=["target_type", "target_id"])]

    def payload(self) -> dict:
        return {
            "at": self.at,
            "actor_id": self.actor_id,
            "actor_label": self.actor_label,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "data": self.data,
        }
