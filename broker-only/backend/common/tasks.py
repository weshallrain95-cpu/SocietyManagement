from celery import shared_task


@shared_task
def relay_outbox() -> int:
    from .events import relay

    return relay()
