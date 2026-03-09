from django.db import models
from core.querysets.society_queryset import SocietyQuerySet


class SocietyManager(models.Manager):

    def get_queryset(self):
        qs = SocietyQuerySet(self.model, using=self._db)
        return qs._apply_society_filter()
        