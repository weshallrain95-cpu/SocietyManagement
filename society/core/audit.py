import json
import hashlib
from Society.models import AuditEvent

def compute_event_hash(event, previous_hash: str) -> str:
    raw = json.dumps({
        "event_id": str(event.event_id),
        "actor": event.actor_id,
        "event_type": event.event_type,
        "object_type": event.object_type,
        "object_id": event.object_id,
        "action": event.action,
        "payload": event.payload,
        "created_at": event.created_at.isoformat(),
        "previous_hash": previous_hash,
    }, sort_keys=True)

    return hashlib.sha256(raw.encode()).hexdigest()
from django.db import transaction

def create_audit_event(
    *,
    actor,
    actor_role,
    event_type,
    object_type,
    object_id,
    action,
    payload,
    ip_address=None,
    user_agent=""
):
    with transaction.atomic():
        last_event = AuditEvent.objects.order_by("-created_at").first()
        previous_hash = last_event.event_hash if last_event else ""

        event = AuditEvent(
            actor=actor,
            actor_role=actor_role,
            event_type=event_type,
            object_type=object_type,
            object_id=str(object_id),
            action=action,
            payload=payload,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
        )
        event.save()

        event.event_hash = compute_event_hash(event, previous_hash)
        AuditEvent.objects.filter(pk=event.pk).update(event_hash=event.event_hash)

        return event
# society/services/audit.py

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
    This is the ONLY place AuditEvent is written.
    """

    AuditEvent.objects.create(
        event_type=event_type,
        domain=domain,
        object_type=object_type,
        object_id=object_id,
        payload=payload,
        actor_id=actor_id,
    )
