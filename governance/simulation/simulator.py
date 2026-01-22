from governance.models import Policy, PolicyRule
from governance.simulation.evaluator import RuleEvaluator


class PolicySimulator:

    @staticmethod
    def simulate(context):
        context_dict = context.as_dict()
        decisions = []

        policies = Policy.objects.filter(is_active=True)

        for policy in policies:
            rules = PolicyRule.objects.filter(policy=policy).order_by("priority")

            for rule in rules:
                if RuleEvaluator.evaluate_condition(rule.condition, context_dict):
                    decision = RuleEvaluator.build_decision(policy, rule, context_dict)
                    decisions.append(decision)
                    break  # first-match per policy

        # global resolution by priority
        decisions.sort(key=lambda d: d.priority)

        return decisions
