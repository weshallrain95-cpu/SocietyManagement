from django.db import models

class CommunicationContext(models.Model):
    """
    Links communication to domain objects
    """
    context_type = models.CharField(max_length=100)  # complaint, notice, document, governance_action
    context_id = models.UUIDField()

    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["context_type", "context_id"]),
        ]
