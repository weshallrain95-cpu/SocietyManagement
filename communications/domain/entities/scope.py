from django.db import models

class CommunicationScope(models.Model):
    """
    Defines isolation boundary
    Example: Society, Committee, Global, Admin
    """
    name = models.CharField(max_length=100, unique=True)
    society_id = models.UUIDField(null=True, blank=True)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["society_id"]),
            models.Index(fields=["name"]),
        ]
