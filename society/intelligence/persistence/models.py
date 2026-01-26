from django.db import models

class IntelligenceMemoryEvent(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    node_id = models.CharField(max_length=128)
    workflow_id = models.CharField(max_length=128, null=True, blank=True)

    event_type = models.CharField(max_length=64)  # success / failure / decision
    payload = models.JSONField()

    risk_score = models.FloatField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["node_id"]),
            models.Index(fields=["workflow_id"]),
            models.Index(fields=["event_type"]),
        ]
