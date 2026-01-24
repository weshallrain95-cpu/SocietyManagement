# society/legal/integration/events/services/event_router.py

from society.legal.integration.events.services.event_validator import EventValidator
from society.legal.integration.events.services.event_signer import EventSigner
from society.legal.integration.events.services.event_audit import EventAuditService


# ============================
# Legal Event Router
# ============================

class LegalEventRouter:
    """
    Central legal event router.
    """

    def __init__(self):
        self.validator = EventValidator()
        self.signer = EventSigner()
        self.audit = EventAuditService()

    def publish(self, event_data: dict):
        # Validate
        self.validator.validate(event_data)

        # Sign
        signed_event = self.signer.sign(event_data)

        # Audit store
        event = self.audit.record(signed_event)

        # Future hooks:
        # - state sync
        # - enforcement triggers
        # - dispute triggers
        # - compliance triggers
        # - governance triggers

        return event
