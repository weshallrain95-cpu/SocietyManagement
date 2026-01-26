from .decision import DecisionContext

class ComplianceEngine:
    def evaluate(self, context: DecisionContext) -> list[str]:
        raise NotImplementedError
