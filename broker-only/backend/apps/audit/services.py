from django.db import connection, transaction
from django.utils import timezone

from common.hashchain import GENESIS, chain_hash

from .models import AuditEvent

_LOCK_KEY = 815_001  # pg advisory lock serialising appends to the chain


def audit(actor, action: str, target, data: dict | None = None, *, actor_label: str = "") -> AuditEvent:
    with transaction.atomic():
        with connection.cursor() as cur:
            cur.execute("SELECT pg_advisory_xact_lock(%s)", [_LOCK_KEY])
        last = AuditEvent.objects.order_by("-seq").only("hash").first()
        ev = AuditEvent(
            at=timezone.now(),
            actor_id=getattr(actor, "pk", None),
            actor_label=actor_label or ("system" if actor is None else ""),
            action=action,
            target_type=target._meta.label_lower if hasattr(target, "_meta") else str(type(target).__name__),
            target_id=str(getattr(target, "pk", target)),
            data=data or {},
            prev_hash=last.hash if last else GENESIS,
        )
        ev.hash = chain_hash(ev.prev_hash, ev.payload())
        ev.save(force_insert=True)
        return ev


def verify_chain() -> dict:
    prev = GENESIS
    count = 0
    for ev in AuditEvent.objects.order_by("seq").iterator(chunk_size=2000):
        # Re-read JSON through the same serialiser used at write time.
        if ev.prev_hash != prev or chain_hash(prev, ev.payload()) != ev.hash:
            return {"ok": False, "checked": count, "broken_at_seq": ev.seq}
        prev = ev.hash
        count += 1
    return {"ok": True, "checked": count, "head": prev}
