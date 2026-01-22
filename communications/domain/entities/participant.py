from django.db import models

class CommunicationParticipant(models.Model):
    """
    Abstract participant layer
    """
    user_id = models.UUIDField()
    role = models.CharField(max_length=100)  # member, committee, admin, vendor
    society_id = models.UUIDField()

    active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["society_id"]),
            models.Index(fields=["role"]),
        ]
