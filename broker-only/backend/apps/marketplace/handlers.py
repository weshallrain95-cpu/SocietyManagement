from common.events import handles


@handles("enquiry.created")
def on_enquiry(payload):
    from .services import broadcast

    broadcast(payload["enquiry_id"])


@handles("unit_status.changed")
def on_status(payload):
    """Debounced: mark the map dirty; the scheduled task rebuilds at most once a minute."""
    from django.core.cache import cache

    cache.set("supply:dirty", True, None)
