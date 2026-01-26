from dataclasses import dataclass

@dataclass
class DecisionContext:
    actor: str | None
    role: str | None
    domain: str
    workflow_type: str
    object_type: str
    object_state: dict
    trust_score: float = 1.0
    risk_score: float = 0.0
    policy_flags: list[str] | None = None
    compliance_flags: list[str] | None = None

@dataclass
class DecisionResult:
    next_step: str
    escalation_level: str | None = None
    required_approvals: list[str] | None = None
    block: bool = False
    reason: str | None = None

class DecisionEngine:
    def evaluate(self, context: DecisionContext) -> DecisionResult:
        raise NotImplementedError
