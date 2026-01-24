# society/legal/integration/events/services/event_validator.py

class EventValidator:
    """
    Validates legal event structure and semantics.
    """

    REQUIRED_FIELDS = [
        "event_id", "intent", "source_platform",
        "jurisdiction", "authority_id", "authority_type",
        "legal_domain", "canon_ref",
        "entity_id", "entity_type",
    ]

    def validate(self, event: dict) -> bool:
        for field in self.REQUIRED_FIELDS:
            if field not in event:
                raise ValueError(f"Missing required field: {field}")

        if not event.get("canon_ref"):
            raise ValueError("Canon binding required")

        if not event.get("authority_id"):
            raise ValueError("Authority binding required")

        return True
