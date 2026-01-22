from django.db import models
from .scope import CommunicationScope

class CommunicationChannel(models.Model):
    """
    Logical channel abstraction
    Example: complaints, notices, governance, documents
    """
    name = models.CharField(max_length=100)
    scope = models.ForeignKey(CommunicationScope, on_delete=models.CASCADE)

    governed = models.BooleanField(default=True)
    moderated = models.BooleanField(default=True)
    audited = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "scope")
