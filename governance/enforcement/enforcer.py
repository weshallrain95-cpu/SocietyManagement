from governance.enforcement.exceptions import GovernanceDenied, GovernanceSoftDenied
from governance.enforcement.resolver import DecisionResolver
from governance.simulation.simulator import PolicySimulator
from governance.audit.emitter import emit_governance_decision


class GovernanceEnforcer:

    @staticmethod
    def enforce(context, *, observe_only=False):
        decisions = PolicySimulator.simulate(context)

        if not decisions:
            return {"effect": "ALLOW", "reason": "No policies matched"}

        final = DecisionResolver.resolve(decisions)

        # AUDIT (always log)
        emit_governance_decision(
            context=context,
            final_decision=final,
            all_decisions=decisions,
        )

        # OBSERVE MODE
        if final.effect == "OBSERVE":
            return {
                "effect": "OBSERVE",
                "decision": final,
                "decisions": decisions,
            }

        # DENY
        if final.effect == "DENY":
            if observe_only:
                return {
                    "effect": "DENY",
                    "mode": "OBSERVE_ONLY",
                    "decision": final,
                    "decisions": decisions,
                }
            raise GovernanceDenied(f"Denied by {final.policy_code}: {final.rule_condition}")

        # SOFT DENY
        if final.effect == "SOFT_DENY":
            if observe_only:
                return {
                    "effect": "SOFT_DENY",
                    "mode": "OBSERVE_ONLY",
                    "decision": final,
                    "decisions": decisions,
                }
            raise GovernanceSoftDenied(f"Soft denied by {final.policy_code}: {final.rule_condition}")

        # ALLOW
        return {
            "effect": "ALLOW",
            "decision": final,
            "decisions": decisions,
        }
