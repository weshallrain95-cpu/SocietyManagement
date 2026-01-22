from society.audit_emitter import emit_audit_event


def emit_governance_decision(*, context, final_decision, all_decisions):
    """
    Records a governance decision into the audit log.
    """

    payload = {
        "actor": context.actor,
        "role": context.role,
        "action": context.action,
        "resource": context.resource,
        "attributes": context.attributes,
        "final_decision": {
            "policy_code": final_decision.policy_code,
            "effect": final_decision.effect,
            "rule": final_decision.rule_condition,
            "priority": final_decision.priority,
            "explanation": final_decision.explanation,
        },
        "all_decisions": [
            {
                "policy_code": d.policy_code,
                "effect": d.effect,
                "rule": d.rule_condition,
                "priority": d.priority,
                "explanation": d.explanation,
            }
            for d in all_decisions
        ],
    }

    emit_audit_event(
        event_type="GOVERNANCE_DECISION",
        domain="GOVERNANCE",
        object_type="POLICY_ENGINE",
        object_id=context.resource,
        payload=payload,
        actor_id=context.actor,
    )
