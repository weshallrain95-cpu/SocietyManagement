# society/audit_verifier.py

from society.models import AuditEvent
from society.audit_emitter import compute_event_hash, GENESIS_HASH


def verify_audit_chain():
    """
    Verifies the integrity of the audit event hash chain.

    Returns:
        (is_valid: bool, error: dict | None)
    """
    previous_hash = GENESIS_HASH
    events = AuditEvent.objects.order_by("created_at")

    for event in events:
        # Legacy trust anchor
        if event.event_hash == GENESIS_HASH:
            previous_hash = GENESIS_HASH
            continue

        payload = {
            "event_type": event.event_type,
            "domain": event.domain,
            "object_type": event.object_type,
            "object_id": event.object_id,
            "payload": event.payload,
            "actor_id": event.actor_id,
        }

        expected_hash = compute_event_hash(
            previous_hash=previous_hash,
            data=payload,
        )

        if event.event_hash != expected_hash:
            return False, {
                "event_id": event.id,
                "expected_hash": expected_hash,
                "actual_hash": event.event_hash,
            }

        previous_hash = event.event_hash

    return True, None
