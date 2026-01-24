# society/legal/integration/events/services/legal_event_store.py

from society.legal.integration.events.models.legal_event import LegalEvent


# ============================
# Legal Event Store
# ============================

class LegalEventStore:
    """
    Persistent storage for legal events.
    """

    def save(self, event_data: dict) -> LegalEvent:
        event = LegalEvent.objects.create(**event_data)
        return event

    def get_by_event_id(self, event_id: str) -> LegalEvent:
        return LegalEvent.objects.get(event_id=event_id)

    def list_by_entity(self, entity_id: str):
        return LegalEvent.objects.filter(entity_id=entity_id).order_by("timestamp")
