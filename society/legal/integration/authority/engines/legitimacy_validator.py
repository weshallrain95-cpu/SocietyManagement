# society/legal/integration/authority/engines/legitimacy_validator.py

class LegitimacyValidator:
    """
    Validates legal legitimacy.
    """

    def validate(self, context: dict) -> bool:
        authority = context.get("authority", {})
        legitimacy = authority.get("legitimacy", {})

        # Must have canon + evidence
        if not legitimacy.get("canon_ref"):
            return False
        if not legitimacy.get("evidence_ref"):
            return False

        return True
