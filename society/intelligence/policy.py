from .decision import DecisionContext

class PolicyEngine:
    def evaluate(self, context: DecisionContext) -> list[str]:
        raise NotImplementedError
