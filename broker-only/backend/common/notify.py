"""Outbound notifications. Providers are pluggable; dev uses the console + WebSocket groups."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction

from .models import Notification

log = logging.getLogger("onlybroker.notify")


def ws_send(group: str, type_: str, data: dict) -> None:
    layer = get_channel_layer()
    if layer is None:
        return

    def _send():
        try:
            async_to_sync(layer.group_send)(group, {"type": "push", "event": type_, "data": data})
        except Exception:  # noqa: BLE001 - realtime is best-effort; push/WhatsApp are the fallback
            log.warning("ws send to %s failed", group, exc_info=True)

    transaction.on_commit(_send)


def notify_org(org_id, template: str, payload: dict, *, realtime_event: str | None = None) -> Notification:
    n = Notification.objects.create(org_id=org_id, template=template, payload=payload, channel="inapp", state="sent")
    ws_send(f"broker.{org_id}", realtime_event or template, payload)
    return n


def notify_user(user, template: str, payload: dict, *, realtime_event: str | None = None) -> Notification:
    n = Notification.objects.create(user=user, template=template, payload=payload, channel="inapp", state="sent")
    ws_send(f"user.{user.pk}", realtime_event or template, payload)
    return n


def send_message(phone_e164: str, template: str, payload: dict, *, phone_hash: str = "", user=None) -> Notification:
    """WhatsApp template with SMS fallback. Console provider in development."""
    provider = settings.OB_NOTIFY_PROVIDER
    n = Notification.objects.create(
        user=user, phone_hash=phone_hash, template=template, payload=payload, channel="whatsapp", state="queued"
    )
    if provider == "console":
        log.warning("DEV MESSAGE [%s] to %s: %s", template, phone_e164[:3] + "…" + phone_e164[-3:], payload)
        n.state = "sent"
        n.save(update_fields=["state"])
        return n
    raise NotImplementedError("WhatsApp Business / SMS providers are wired at staging")


def queue_for_admin(kind: str, ref, summary: str, data: dict | None = None):
    from .models import ReviewQueueItem

    return ReviewQueueItem.objects.create(
        kind=kind,
        ref_type=ref._meta.label_lower if hasattr(ref, "_meta") else "",
        ref_id=str(getattr(ref, "pk", ref)),
        summary=summary[:300],
        data=data or {},
    )
