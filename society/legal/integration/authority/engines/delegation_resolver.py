# society/legal/integration/authority/engines/delegation_resolver.py

class DelegationResolver:
    """
    Validates delegated authority.
    """

    def validate(self, context: dict) -> bool:
        authority = context.get("authority", {})

        if authority.get("delegated_from") is None:
            return True

        # delegated authority must have explicit scope
        scope = authority.get("scope", {})
        return scope.get("can_delegate", False) is True
