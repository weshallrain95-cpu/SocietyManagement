import hashlib
import json
from society.models import AuditEvent


def compute_event_hash(event, previous_hash=""):
    """
    Chain-aware cryptographic event hash.
    Supports:
    - dict payloads
    - model instances
    """

    if hasattr(event, "__dict__"):
        # Model instance
        payload = {
            "event_type": event.event_type,
            "domain": event.domain,
            "object_type": event.object_type,
            "object_id": event.object_id,
            "payload": event.payload,
            "previous_hash": previous_hash or "",
        }
    else:
        # Raw dict
        payload = dict(event)
        payload["previous_hash"] = previous_hash or ""

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_audit_event(
    actor,
    actor_role,
    event_type,
    object_type,
    object_id,
    action,
    payload,
    domain="core",
):
    last_event = AuditEvent.objects.order_by("-id").first()
    previous_hash = last_event.event_hash if last_event else ""

    hash_payload = {
        "event_type": event_type,
        "domain": domain,
        "object_type": object_type,
        "object_id": object_id,
        "action": action,
        "payload": payload,
    }

    event_hash = compute_event_hash(hash_payload, previous_hash)

    event = AuditEvent.objects.create(
    event_type=event_type,
    actor_id=str(actor) if actor else None,
    domain=domain,
    object_type=object_type,
    object_id=object_id,
    payload={
        "actor_role": actor_role,
        "action": action,
        "data": payload,
    },
    previous_hash=previous_hash,   # ✅ STORE CHAIN LINK
    event_hash=event_hash,
)

    return event
