"""Broker presence (MKT-11): a heartbeat every ~60 s keeps a broker 'online' for 10 minutes."""

from django.conf import settings
from django.core.cache import cache


def _key(org_id):
    return f"presence:{org_id}"


def heartbeat(org_id, user_id) -> None:
    members = cache.get(_key(org_id)) or {}
    import time

    now = time.time()
    ttl = settings.OB_MARKET["presence_ttl_s"]
    members = {u: t for u, t in members.items() if now - t < ttl}
    members[str(user_id)] = now
    cache.set(_key(org_id), members, ttl)


def go_offline(org_id, user_id) -> None:
    members = cache.get(_key(org_id)) or {}
    members.pop(str(user_id), None)
    cache.set(_key(org_id), members, settings.OB_MARKET["presence_ttl_s"])


def is_online(org_id) -> bool:
    import time

    members = cache.get(_key(org_id)) or {}
    return any(time.time() - t < settings.OB_MARKET["presence_ttl_s"] for t in members.values())
