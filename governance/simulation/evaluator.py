from governance.simulation.decision import SimulationDecision


class RuleEvaluator:

    @staticmethod
    def evaluate_condition(condition: str, context: dict) -> bool:
        if condition.strip() == "True":
            return True

        try:
            return bool(eval(condition, {}, context))
        except Exception:
            return False

    @staticmethod
    def build_decision(policy, rule, context_dict):
        return SimulationDecision(
            policy_code=policy.code,
            effect=rule.effect,
            rule_condition=rule.condition,
            priority=rule.priority,
            explanation=f"Matched rule: {rule.condition}"
        )
