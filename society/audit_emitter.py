# society/audit_emitter.py

from society.models import AuditEvent
import hashlib
import json

GENESIS_HASH = "GENESIS"

def compute_event_hash(*, previous_hash: str, data: dict) -> str:
    """
    Computes a deterministic SHA256 hash for an audit event.
    """
    payload = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
    )
    raw = f"{previous_hash}{payload}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

from society.models import AuditEvent

def emit_audit_event(
    *,
    event_type: str,
    domain: str,
    object_type: str,
    object_id: str,
    payload: dict,
    actor_id: str | None = None,
):
    last = (
        AuditEvent.objects
        .order_by("-created_at")
        .first()
    )

    previous_hash = last.event_hash if last else GENESIS_HASH

    event_payload = {
        "event_type": event_type,
        "domain": domain,
        "object_type": object_type,
        "object_id": object_id,
        "payload": payload,
        "actor_id": actor_id,
    }

    event_hash = compute_event_hash(
        previous_hash=previous_hash,
        data=event_payload,
    )

    AuditEvent.objects.create(
        event_type=event_type,
        domain=domain,
        object_type=object_type,
        object_id=object_id,
        payload=payload,
        actor_id=actor_id,
        event_hash=event_hash,
    )

