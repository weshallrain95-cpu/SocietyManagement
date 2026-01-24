# society/legal/integration/authority/engines/supremacy_resolver.py

class SupremacyResolver:
    """
    Validates hierarchical supremacy.
    """

    def validate(self, context: dict) -> bool:
        authority = context.get("authority", {})
        required_rank = context.get("required_supremacy_rank", None)

        if required_rank is None:
            return True

        return authority.get("supremacy_rank", 999) <= required_rank
