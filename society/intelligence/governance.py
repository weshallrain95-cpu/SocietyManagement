from .decision import DecisionContext

class GovernanceEngine:
    def authorize(self, context: DecisionContext) -> bool:
        raise NotImplementedError
