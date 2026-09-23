"""Transactional outbox: ``emit`` inside the business transaction, handlers run after commit."""
import logging
from collections import defaultdict
from collections.abc import Callable

from django.db import transaction
from django.utils import timezone

from .models import DomainEvent
from .rls import platform_context

log = logging.getLogger(__name__)
_handlers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)


def handles(name: str):
    def deco(fn):
        _handlers[name].append(fn)
        return fn

    return deco


def emit(name: str, **payload) -> DomainEvent:
    event = DomainEvent.objects.create(name=name, payload=_jsonable(payload))

    def _kick():
        from .tasks import relay_outbox

        relay_outbox.delay()

    transaction.on_commit(_kick)
    return event


def _jsonable(payload: dict) -> dict:
    out = {}
    for k, v in payload.items():
        if hasattr(v, "hex") and not isinstance(v, (bytes, str)):
            out[k] = str(v)
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def relay(batch: int = 100) -> int:
    """Process pending events. Safe to run concurrently (SKIP LOCKED)."""
    done = 0
    with platform_context():
        events = list(
            DomainEvent.objects.select_for_update(skip_locked=True)
            .filter(processed_at__isnull=True, attempts__lt=10)
            .order_by("id")[:batch]
        )
        for ev in events:
            try:
                with transaction.atomic():
                    for fn in _handlers.get(ev.name, []):
                        fn(ev.payload)
                ev.processed_at = timezone.now()
                ev.last_error = ""
            except Exception as exc:  # noqa: BLE001 - recorded and retried
                log.exception("outbox handler failed for %s", ev.name)
                ev.last_error = repr(exc)[:2000]
            ev.attempts += 1
            ev.save(update_fields=["processed_at", "attempts", "last_error"])
            done += 1
    return done
