# society/legal/integration/platform/services/legal_pipeline.py

from society.legal.integration.platform.services.legal_action_gateway import LegalActionGateway


class LegalPipeline:
    """
    End-to-end legal execution pipeline.
    """

    def __init__(self):
        self.gateway = LegalActionGateway()

    def execute(self, action_context: dict, event_data: dict):
        return self.gateway.submit(action_context, event_data)
