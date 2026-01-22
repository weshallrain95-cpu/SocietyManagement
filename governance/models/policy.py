from django.db import models
import uuid

class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField()
    scope = models.CharField(max_length=100)
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateTimeField(null=True, blank=True)
    effective_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("code", "version")

    def __str__(self):
        return f"{self.code}@v{self.version}"
