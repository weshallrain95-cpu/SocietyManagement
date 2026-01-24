# society/legal/compliance/services/violation_service.py

from django.utils import timezone
from society.legal.compliance.models.violation import Violation


# ============================
# Violation Service
# ============================

class ViolationService:
    """
    Manages violation lifecycle.
    """

    # ----------------------------
    # State Transitions
    # ----------------------------

    def mark_under_review(self, violation_id):
        v = Violation.objects.get(id=violation_id)
        v.status = "UNDER_REVIEW"
        v.save()
        return v

    def enforce(self, violation_id, actions: dict):
        v = Violation.objects.get(id=violation_id)
        v.status = "ENFORCED"
        v.enforcement_actions = actions
        v.resolved_at = timezone.now()
        v.save()
        return v

    def resolve(self, violation_id):
        v = Violation.objects.get(id=violation_id)
        v.status = "RESOLVED"
        v.resolved_at = timezone.now()
        v.save()
        return v

    def dismiss(self, violation_id):
        v = Violation.objects.get(id=violation_id)
        v.status = "DISMISSED"
        v.resolved_at = timezone.now()
        v.save()
        return v
