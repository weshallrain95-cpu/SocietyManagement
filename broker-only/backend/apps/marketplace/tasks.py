from celery import shared_task
from django.db import transaction

from common.rls import platform_context


@shared_task
def expire_enquiries() -> int:
    from .services import expire_enquiries as run

    with transaction.atomic():
        return run()


@shared_task
def rebuild_supply(force: bool = False) -> int:
    from django.core.cache import cache

    from .supply import rebuild

    if not force and not cache.get("supply:dirty"):
        return 0
    cache.delete("supply:dirty")
    with transaction.atomic(), platform_context():
        return rebuild()
