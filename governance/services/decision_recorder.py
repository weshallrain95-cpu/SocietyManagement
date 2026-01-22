from governance.models import PolicyDecisionLog
from governance.services.policy_types import PolicyDecision, PolicyContext

# Phase 8 audit bridge (optional and safe)
try:
    from society.audit_emitter import emit_audit_event
except ImportError:
    emit_audit_event = None


class PolicyDecisionRecorder:
    """
    Persists policy decisions in a deterministic, auditable way.
    """

    @staticmethod
    def record(
        decision: PolicyDecision,
        context: PolicyContext
    ) -> PolicyDecisionLog:
        """
        Persist a policy decision and optionally emit an audit event.
        """

        log = PolicyDecisionLog.objects.create(
            policy_code=decision.policy_code,
            policy_version=decision.policy_version,
            actor_id=context.actor_id,
            action=context.action,
            resource=context.resource,
            decision="ALLOW" if decision.allowed else "DENY",
            reason=decision.reason,
            decision_hash=decision.decision_hash,
        )

        # ---- Phase 8 Audit Bridge (Correct & Safe) ----
        if emit_audit_event:
            emit_audit_event(
                event_type="POLICY_DECISION",
                domain="GOVERNANCE",
                object_type="PolicyDecision",
                object_id=decision.decision_hash,
                payload={
                    "policy_code": decision.policy_code,
                    "policy_version": decision.policy_version,
                    "decision": decision.allowed,
                    "reason": decision.reason,
                    "action": context.action,
                    "resource": context.resource,
                },
                actor_id=context.actor_id,
            )

        # 🔴 THIS LINE MUST EXIST AND MUST BE HERE
        return log


        # ---- Phase 8 Audit Bridge (Correct & Safe) ----
        if emit_audit_event:
            emit_audit_event(
            event_type="POLICY_DECISION",
            domain="GOVERNANCE",
            object_type="PolicyDecision",
            object_id=decision.decision_hash,
            payload={
                "policy_code": decision.policy_code,
                "policy_version": decision.policy_version,
                "decision": decision.allowed,
                "reason": decision.reason,
                "action": context.action,
                "resource": context.resource,
            },
            actor_id=context.actor_id,
        )
