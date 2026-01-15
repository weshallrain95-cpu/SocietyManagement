import json
import hashlib
from django.db import transaction
from society.models import AuditEvent


def compute_event_hash(event, previous_hash: str) -> str:
    raw = json.dumps(
        {
            "event_id": str(event.event_id),
            "actor": event.actor_id,
            "actor_role": event.actor_role,
            "event_type": event.event_type,
            "object_type": event.object_type,
            "object_id": event.object_id,
            "action": event.action,
            "payload": event.payload,
            "previous_hash": previous_hash,
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def create_audit_event(
    *,
    actor,
    actor_role,
    event_type,
    object_type,
    object_id,
    action,
    payload,
):
    with transaction.atomic():
        last_event = AuditEvent.objects.order_by("-pk").first()

        previous_hash = last_event.event_hash if last_event else ""

        event = AuditEvent.objects.create(
            actor=actor,
            actor_role=actor_role,
            event_type=event_type,
            object_type=object_type,
            object_id=str(object_id),
            action=action,
            payload=payload,
            previous_hash=previous_hash,
        )

        event.event_hash = compute_event_hash(event, previous_hash)
        AuditEvent.objects.filter(pk=event.pk).update(
            event_hash=event.event_hash
        )

        return event

