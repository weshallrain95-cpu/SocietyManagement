from .jurisdiction_resolver import JurisdictionResolver
from .supremacy_resolver import SupremacyResolver
from .delegation_resolver import DelegationResolver
from .legitimacy_validator import LegitimacyValidator
from .conflict_resolver import ConflictResolver


# ============================
# Authority Resolver
# ============================

class AuthorityResolver:
    """
    Central authority resolution engine.
    Determines if an action is legally authorized.
    """

    def __init__(self):
        self.jurisdiction_resolver = JurisdictionResolver()
        self.supremacy_resolver = SupremacyResolver()
        self.delegation_resolver = DelegationResolver()
        self.legitimacy_validator = LegitimacyValidator()
        self.conflict_resolver = ConflictResolver()

    def resolve(self, action_context: dict) -> dict:
        """
        action_context must contain:
        - authority
        - jurisdiction
        - legal_domain
        - canon_ref
        - action
        """

        # Step 1: Jurisdiction check
        if not self.jurisdiction_resolver.validate(action_context):
            return {"authorized": False, "reason": "JURISDICTION_VIOLATION"}

        # Step 2: Legitimacy check
        if not self.legitimacy_validator.validate(action_context):
            return {"authorized": False, "reason": "LEGITIMACY_INVALID"}

        # Step 3: Delegation check
        if not self.delegation_resolver.validate(action_context):
            return {"authorized": False, "reason": "INVALID_DELEGATION"}

        # Step 4: Supremacy check
        if not self.supremacy_resolver.validate(action_context):
            return {"authorized": False, "reason": "SUPREMACY_VIOLATION"}

        return {
            "authorized": True,
            "authority": action_context.get("authority"),
            "jurisdiction": action_context.get("jurisdiction"),
            "legal_domain": action_context.get("legal_domain"),
        }
