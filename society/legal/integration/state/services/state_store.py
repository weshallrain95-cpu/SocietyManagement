# society/legal/integration/state/services/state_store.py

from society.legal.integration.state.models.legal_state import LegalState


class LegalStateStore:
    """
    Persistent store for legal states.
    """

    def get(self, entity_id: str, entity_type: str):
        return LegalState.objects.filter(
            entity_id=entity_id,
            entity_type=entity_type
        ).first()

    def save(self, state_data: dict) -> LegalState:
        obj, _ = LegalState.objects.update_or_create(
            entity_id=state_data["entity_id"],
            entity_type=state_data["entity_type"],
            defaults=state_data
        )
        return obj

    def list_by_domain(self, legal_domain: str):
        return LegalState.objects.filter(legal_domain=legal_domain)
