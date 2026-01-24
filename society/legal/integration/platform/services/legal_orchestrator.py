# society/legal/integration/platform/services/legal_orchestrator.py

from society.legal.integration.platform.services.legal_platform_core import LegalPlatformCore


class LegalOrchestrator:
    """
    High-level legal orchestration engine.
    """

    def __init__(self):
        self.core = LegalPlatformCore()

    def process(self, action_context: dict, event_data: dict):
        return self.core.execute_legal_action(action_context, event_data)
