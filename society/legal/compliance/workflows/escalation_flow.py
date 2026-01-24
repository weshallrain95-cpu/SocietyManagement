# society/legal/compliance/workflows/escalation_flow.py

from datetime import datetime


# ============================
# Escalation Flow
# ============================

class EscalationFlow:
    """
    Handles governance and legal escalation.
    """

    def initiate(self, entity_id: str, violation, severity: str, context: dict) -> dict:
        """
        Starts escalation process.
        """

        level = "LOW"

        if severity == "HIGH":
            level = "CRITICAL"
        elif severity == "MEDIUM":
            level = "MAJOR"

        return {
            "flow_type": "ESCALATION",
            "entity_id": entity_id,
            "violation": violation.id if hasattr(violation, "id") else str(violation),
            "severity": severity,
            "level": level,
            "steps": [
                "GOVERNANCE_NOTIFICATION",
                "LEGAL_REVIEW",
                "ENFORCEMENT_REVIEW",
                "DECISION_PANEL",
                "FINAL_ACTION",
            ],
            "started_at": datetime.utcnow(),
            "status": "ACTIVE",
            "context": context,
        }
