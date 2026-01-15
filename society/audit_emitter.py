# society/audit_emitter.py

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
    """
    Canonical audit event emitter.
    Single write-path for audit events.
    """
    AuditEvent.objects.create(
        event_type=event_type,
        domain=domain,
        object_type=object_type,
        object_id=object_id,
        payload=payload,
        actor_id=actor_id,
    )
