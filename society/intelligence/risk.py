from .decision import DecisionContext

class RiskEngine:
    def score(self, context: DecisionContext) -> float:
        raise NotImplementedError
