# society/legal/integration/events/services/event_audit.py

from society.legal.integration.events.services.legal_event_store import LegalEventStore


# ============================
# Event Audit Service
# ============================

class EventAuditService:
    """
    Immutable legal audit trail.
    """

    def __init__(self):
        self.store = LegalEventStore()

    def record(self, event_data: dict):
        return self.store.save(event_data)
