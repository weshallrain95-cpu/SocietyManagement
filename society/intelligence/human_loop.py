from .decision import DecisionContext

class HumanLoopEngine:
    def require_approval(self, context: DecisionContext, roles: list[str]):
        raise NotImplementedError
