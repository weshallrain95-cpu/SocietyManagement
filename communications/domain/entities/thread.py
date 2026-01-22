from django.db import models
from .channel import CommunicationChannel
from .context import CommunicationContext

class CommunicationThread(models.Model):
    """
    Root aggregate for communication
    """
    title = models.CharField(max_length=255)
    channel = models.ForeignKey(CommunicationChannel, on_delete=models.CASCADE)
    context = models.ForeignKey(CommunicationContext, on_delete=models.SET_NULL, null=True, blank=True)

    society_id = models.UUIDField()
    locked = models.BooleanField(default=False)
    governed = models.BooleanField(default=True)

    created_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["society_id"]),
            models.Index(fields=["created_by"]),
        ]
