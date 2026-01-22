from django.db import models
from .thread import CommunicationThread
from .participant import CommunicationParticipant

class CommunicationMessage(models.Model):
    """
    Atomic communication unit
    """
    thread = models.ForeignKey(CommunicationThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CommunicationParticipant, on_delete=models.CASCADE)

    content = models.TextField()
    content_type = models.CharField(max_length=50, default="text")  # text, file, system

    moderated = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    compliance_checked = models.BooleanField(default=False)

    governance_decision = models.CharField(max_length=50, null=True, blank=True)  # allow/block/escalate

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["moderated"]),
            models.Index(fields=["blocked"]),
        ]
