from django.db import models
from core.context.society_context import get_current_society


class SocietyQuerySet(models.QuerySet):

    def _apply_society_filter(self):
        society = get_current_society()

        if not society:
            return self

        # Only filter models that actually have a society field
        field_names = [f.name for f in self.model._meta.fields]

        if "society" in field_names:
            return super().filter(society=society)

        return self

    def all(self):
        qs = super().all()
        return qs._apply_society_filter()

    def filter(self, *args, **kwargs):
        qs = super().filter(*args, **kwargs)
        return qs._apply_society_filter()

    def update(self, **kwargs):
        qs = self._apply_society_filter()
        return super(SocietyQuerySet, qs).update(**kwargs)

    def delete(self):
        qs = self._apply_society_filter()
        return super(SocietyQuerySet, qs).delete()
