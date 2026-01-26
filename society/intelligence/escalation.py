from .decision import DecisionContext

class EscalationEngine:
    def escalate(self, context: DecisionContext, level: str):
        raise NotImplementedError
