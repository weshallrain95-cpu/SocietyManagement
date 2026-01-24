# society/legal/constitution/services/bylaw_engine.py

from typing import List
from django.utils import timezone

from society.legal.constitution.models.bylaw import Bylaw


# ============================
# Bylaw Execution Engine
# ============================

class BylawEngine:
    """
    Executes and evaluates bylaws.
    Core enforcement logic layer.
    """

    def get_active_bylaws(self) -> List[Bylaw]:
        now = timezone.now()
        return Bylaw.objects.filter(
            status="ACTIVE",
            effective_from__lte=now
        ).filter(
            models.Q(effective_until__isnull=True) |
            models.Q(effective_until__gte=now)
        )

    def evaluate_bylaw(self, bylaw: Bylaw, context: dict) -> dict:
        """
        Evaluates bylaw against a context.
        Returns enforcement decision.
        """

        if not bylaw.is_enforceable():
            return {
                "enforce": False,
                "reason": "Bylaw not active"
            }

        payload = bylaw.get_normative_payload()

        # Placeholder logic engine (future AI / rule engine)
        decision = {
            "enforce": True,
            "bylaw": bylaw.code,
            "normative_type": payload["normative_type"],
            "sanctions": payload.get("sanctions", []),
            "enforcement_hooks": payload.get("enforcement_hooks", {}),
        }

        return decision

    def enforce(self, bylaw: Bylaw, context: dict) -> dict:
        decision = self.evaluate_bylaw(bylaw, context)
        if decision["enforce"]:
            # Hook into enforcement engine (Phase 11.3+)
            return {
                "status": "ENFORCED",
                "decision": decision
            }
        return {
            "status": "NOT_ENFORCED",
            "decision": decision
        }
