# society/legal/integration/platform/services/legal_action_gateway.py

from society.legal.integration.platform.services.legal_orchestrator import LegalOrchestrator


class LegalActionGateway:
    """
    Entry gateway for all legal actions.
    """

    def __init__(self):
        self.orchestrator = LegalOrchestrator()

    def submit(self, action_context: dict, event_data: dict):
        """
        Single entry point into legal system.
        """
        return self.orchestrator.process(action_context, event_data)
