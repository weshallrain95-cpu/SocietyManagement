from celery import shared_task
from django.db import transaction

from common.rls import platform_context


@shared_task
def decay_stale_statuses() -> int:
    from .services import decay_stale

    with transaction.atomic(), platform_context():
        return decay_stale()
