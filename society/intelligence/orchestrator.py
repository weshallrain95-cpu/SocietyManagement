from .decision import DecisionContext, DecisionResult
from .decision import DecisionEngine
from .policy import PolicyEngine
from .sla import SLAEngine
from .escalation import EscalationEngine
from .compliance import ComplianceEngine
from .governance import GovernanceEngine
from .human_loop import HumanLoopEngine
from .trust import TrustEngine
from .risk import RiskEngine
from .observability import ObservabilityEngine


class WorkflowIntelligenceOrchestrator:
    def __init__(
        self,
        decision: DecisionEngine,
        policy: PolicyEngine,
        sla: SLAEngine,
        escalation: EscalationEngine,
        compliance: ComplianceEngine,
        governance: GovernanceEngine,
        human_loop: HumanLoopEngine,
        trust: TrustEngine,
        risk: RiskEngine,
        observability: ObservabilityEngine,
    ):
        self.decision = decision
        self.policy = policy
        self.sla = sla
        self.escalation = escalation
        self.compliance = compliance
        self.governance = governance
        self.human_loop = human_loop
        self.trust = trust
        self.risk = risk
        self.observability = observability

    def evaluate(self, context: DecisionContext) -> DecisionResult:
        context.trust_score = self.trust.score(context.actor)
        context.risk_score = self.risk.score(context)

        context.policy_flags = self.policy.evaluate(context)
        context.compliance_flags = self.compliance.evaluate(context)

        if not self.governance.authorize(context):
            return DecisionResult(
                next_step="BLOCKED",
                block=True,
                reason="Governance authorization failed",
            )

        decision = self.decision.evaluate(context)

        if decision.required_approvals:
            self.human_loop.require_approval(context, decision.required_approvals)

        if decision.escalation_level:
            self.escalation.escalate(context, decision.escalation_level)

        self.observability.record(
            workflow_id=context.workflow_type,
            data={
                "decision": decision.next_step,
                "trust": context.trust_score,
                "risk": context.risk_score,
                "policy": context.policy_flags,
                "compliance": context.compliance_flags,
            },
        )

        return decision
