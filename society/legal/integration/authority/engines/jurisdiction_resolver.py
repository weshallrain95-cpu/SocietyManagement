# society/legal/integration/authority/engines/jurisdiction_resolver.py

class JurisdictionResolver:
    """
    Validates jurisdictional authority.
    """

    def validate(self, context: dict) -> bool:
        authority = context.get("authority", {})
        jurisdiction = context.get("jurisdiction")

        allowed = authority.get("jurisdiction")

        if allowed is None:
            return False

        return jurisdiction == allowed or allowed == "global"
