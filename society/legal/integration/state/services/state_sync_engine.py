# society/legal/integration/state/services/state_sync_engine.py

from society.legal.integration.state.services.state_projection import StateProjectionEngine
from society.legal.integration.state.services.state_store import LegalStateStore
from society.legal.integration.state.services.state_conflict_resolver import StateConflictResolver


class StateSyncEngine:
    """
    Synchronizes legal state from legal events.
    """

    def __init__(self):
        self.projector = StateProjectionEngine()
        self.store = LegalStateStore()
        self.resolver = StateConflictResolver()

    def sync(self, event: dict):
        current = self.store.get(event["entity_id"], event["entity_type"])
        current_data = current.__dict__ if current else None

        projected = self.projector.project(event, current_data)

        if current_data:
            resolved = self.resolver.resolve(current_data, projected)
        else:
            resolved = projected

        return self.store.save(resolved)
