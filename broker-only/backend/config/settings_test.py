"""Settings for the automated test suite: in-memory channels/cache, eager Celery, dev keys."""

import os

for k, v in {
    "DJANGO_DEBUG": "true",
    "CHANNELS_IN_MEMORY": "true",
    "CACHE_IN_MEMORY": "true",
    "CELERY_TASK_ALWAYS_EAGER": "true",
}.items():
    os.environ.setdefault(k, v)

from .settings import *  # noqa: E402,F403

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
