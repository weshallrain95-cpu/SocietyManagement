class DecisionResolver:

    PRIORITY_ORDER = {
        "DENY": 1,
        "SOFT_DENY": 2,
        "ALLOW": 3,
        "OBSERVE": 4,
    }

    @staticmethod
    def resolve(decisions):
        if not decisions:
            return None

        # Sort by effect severity then by priority
        decisions_sorted = sorted(
            decisions,
            key=lambda d: (DecisionResolver.PRIORITY_ORDER.get(d.effect, 99), d.priority)
        )

        return decisions_sorted[0]
