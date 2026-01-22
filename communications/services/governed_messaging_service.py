from communications.engines.communication_engine import CommunicationEngine
from communications.engines.moderation_engine import ModerationEngine
from communications.engines.compliance_engine import ComplianceEngine
from communications.engines.routing_engine import RoutingEngine

from communications.governance_hooks.policy_adapter import CommunicationsPolicyAdapter
from communications.governance_hooks.audit_adapter import CommunicationsAuditAdapter
from communications.governance_hooks.enforcement_adapter import CommunicationsEnforcementAdapter
from communications.governance_hooks.versioning_adapter import CommunicationsVersioningAdapter


class GovernedMessagingService:
    """
    Central orchestrator for governed communications
    """

    def __init__(self):
        self.policy = CommunicationsPolicyAdapter()
        self.audit = CommunicationsAuditAdapter()
        self.enforcement = CommunicationsEnforcementAdapter()
        self.versioning = CommunicationsVersioningAdapter()

        self.comm_engine = CommunicationEngine()
        self.moderation_engine = ModerationEngine()
        self.compliance_engine = ComplianceEngine()
        self.routing_engine = RoutingEngine()

    def send_message(self, sender, content, context):
        """
        Governed message pipeline
        """

        # 1. Policy Evaluation
        policy_decision = self.policy.evaluate(
            context=context,
            action="send_message",
            actor=sender
        )

        if not policy_decision:
            self.audit.log_event(
                event_type="MESSAGE_BLOCKED_POLICY",
                payload={"sender": str(sender), "context": context},
                actor=sender
            )
            return {"status": "blocked", "reason": "policy"}

        # 2. Governance Enforcement
        enforcement_decision = self.enforcement.enforce(
            decision="allow",
            context=context
        )

        if enforcement_decision != "allow":
            self.audit.log_event(
                event_type="MESSAGE_BLOCKED_ENFORCEMENT",
                payload={"sender": str(sender), "context": context},
                actor=sender
            )
            return {"status": "blocked", "reason": "enforcement"}

        # 3. Moderation
        moderation_result = self.moderation_engine.evaluate(
            message=content,
            context=context
        )

        if not moderation_result.get("allowed", True):
            self.audit.log_event(
                event_type="MESSAGE_BLOCKED_MODERATION",
                payload={"sender": str(sender), "content": content},
                actor=sender
            )
            return {"status": "blocked", "reason": "moderation"}

        # 4. Compliance
        compliance_ok = self.compliance_engine.validate(
            message=content,
            context=context
        )

        if not compliance_ok:
            self.audit.log_event(
                event_type="MESSAGE_BLOCKED_COMPLIANCE",
                payload={"sender": str(sender), "content": content},
                actor=sender
            )
            return {"status": "blocked", "reason": "compliance"}

        # 5. Routing
        recipients = self.routing_engine.resolve_recipients(
            sender=sender,
            context=context
        )

        # 6. Send
        message_obj = self.comm_engine.send_message({
            "sender": sender,
            "content": content,
            "context": context,
            "recipients": recipients
        })

        # 7. Audit
        self.audit.log_event(
            event_type="MESSAGE_SENT",
            payload={"message": str(message_obj)},
            actor=sender
        )

        # 8. Versioning
        self.versioning.version_event(
            obj=message_obj,
            action="create"
        )

        return {"status": "sent", "message": message_obj}
