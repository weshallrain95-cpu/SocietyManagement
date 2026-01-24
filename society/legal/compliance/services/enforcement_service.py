# society/legal/compliance/services/enforcement_service.py

from society.legal.compliance.engines.enforcement_engine import EnforcementEngine
from society.legal.compliance.services.violation_service import ViolationService


# ============================
# Enforcement Service
# ============================

class EnforcementService:
    """
    Executes enforcement actions and workflows.
    """

    def __init__(self):
        self.engine = EnforcementEngine()
        self.violation_service = ViolationService()

    # ----------------------------
    # Enforcement Pipeline
    # ----------------------------

    def enforce_violations(self, violations):
        """
        Enforces a list of violations.
        """

        actions = self.engine.enforce(violations)

        enforced = []

        for action in actions:
            violation = action["violation"]

            # Persist enforcement
            v_model = self.violation_service.enforce(
                violation_id=violation.context.get("violation_id"),
                actions=action
            )

            # Hooks for:
            # - communications platform
            # - governance enforcement
            # - workflow engine
            # - arbitration engine
            # - compliance workflows
            # - audit pipeline

            enforced.append({
                "violation": v_model,
                "action": action,
            })

        return enforced
