# society/legal/integration/authority/engines/conflict_resolver.py

class ConflictResolver:
    """
    Resolves conflicts between authorities.
    """

    def resolve(self, authority_a: dict, authority_b: dict) -> dict:
        # Higher supremacy rank wins
        if authority_a.get("supremacy_rank", 999) < authority_b.get("supremacy_rank", 999):
            return authority_a
        if authority_b.get("supremacy_rank", 999) < authority_a.get("supremacy_rank", 999):
            return authority_b

        # Canon strength fallback
        canon_a = authority_a.get("legitimacy", {}).get("canon_ref")
        canon_b = authority_b.get("legitimacy", {}).get("canon_ref")

        if canon_a and not canon_b:
            return authority_a
        if canon_b and not canon_a:
            return authority_b

        # Default: first authority
        return authority_a
