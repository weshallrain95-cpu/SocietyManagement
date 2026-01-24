# society/legal/integration/state/services/state_projection.py

class StateProjectionEngine:
    """
    Projects legal events into legal state.
    """

    def project(self, event: dict, current_state: dict | None) -> dict:
        if not current_state:
            current_state = {}

        # Basic projection
        current_state["entity_id"] = event.get("entity_id")
        current_state["entity_type"] = event.get("entity_type")
        current_state["jurisdiction"] = event.get("jurisdiction")
        current_state["legal_domain"] = event.get("legal_domain")

        # Legal status transition
        if event.get("state_to"):
            current_state["legal_status"] = event.get("state_to")
        else:
            current_state.setdefault("legal_status", "VALID")

        # Authority
        current_state["authority_state"] = {
            "authority_id": event.get("authority_id"),
            "authority_type": event.get("authority_type"),
            "supremacy_rank": event.get("supremacy_rank"),
        }

        # Canon
        current_state["canon_state"] = {
            "canon_ref": event.get("canon_ref"),
            "binding": "MANDATORY"
        }

        # Compliance
        current_state["compliance_state"] = event.get("compliance_context", {})

        # Enforcement
        current_state["enforcement_state"] = event.get("enforcement_context", {})

        # Evidence
        current_state["evidence_state"] = {
            "refs": event.get("evidence_refs", []),
            "integrity": "VALID"
        }

        # Audit
        current_state["audit_state"] = {
            "last_event": event.get("event_id"),
            "hash": event.get("hash"),
        }

        current_state["last_event_id"] = event.get("event_id")

        return current_state
