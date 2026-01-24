from society.legal.integration.authority.engines.authority_resolver import AuthorityResolver
from society.legal.integration.events.services.event_router import LegalEventRouter
from society.legal.integration.state.services.state_sync_engine import StateSyncEngine


class LegalPlatformCore:
    """
    Central legal platform core.
    """

    def __init__(self):
        self.authority_engine = AuthorityResolver()
        self.event_bus = LegalEventRouter()
        self.state_engine = StateSyncEngine()

    def execute_legal_action(self, action_context: dict, event_data: dict):
        """
        Full legal execution pipeline:
        Authority → Event → State → System
        """

        # 1. Authority resolution
        authority_result = self.authority_engine.resolve(action_context)
        if not authority_result.get("authorized"):
            return {
                "status": "DENIED",
                "reason": authority_result.get("reason")
            }

        # 2. Publish legal event
        event = self.event_bus.publish(event_data)

        # 3. Sync legal state
        state = self.state_engine.sync(event_data)

        return {
            "status": "EXECUTED",
            "event_id": event.event_id,
            "state_id": state.id,
            "legal_status": state.legal_status
        }
