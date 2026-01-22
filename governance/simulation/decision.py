from dataclasses import dataclass


@dataclass
class SimulationDecision:
    policy_code: str
    effect: str
    rule_condition: str
    priority: int
    explanation: str
