import hashlib
import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from common import crypto

from .models import OtpChallenge

log = logging.getLogger("onlybroker.otp")
TTL = timedelta(minutes=5)
MAX_ATTEMPTS = 5
WINDOW_S = 15 * 60


class OtpError(Exception):
    pass


def _hash(code: str, phone_hash: str) -> str:
    return hashlib.sha256(f"{phone_hash}:{code}".encode()).hexdigest()


def request_otp(phone: str) -> str | None:
    """Create a challenge and send it. Returns the code only for the dev console provider."""
    e164 = crypto.normalise_phone(phone)
    ph = crypto.phone_hash(e164)
    key = f"otp-req:{ph}"
    count = cache.get(key, 0)
    if count >= MAX_ATTEMPTS:
        raise OtpError("Too many OTP requests. Try again in 15 minutes.")
    cache.set(key, count + 1, WINDOW_S)
    code = f"{secrets.randbelow(10**6):06d}"
    OtpChallenge.objects.create(phone_hash=ph, code_hash=_hash(code, ph), expires_at=timezone.now() + TTL)
    if settings.OB_OTP_PROVIDER == "console":
        log.warning("DEV OTP for %s: %s", crypto.mask_phone(e164), code)
        return code if settings.OB_EXPOSE_DEV_OTP else None
    raise NotImplementedError("SMS provider integration (MSG91/Exotel) is configured at staging")


def verify_otp(phone: str, code: str) -> str:
    """Return the phone hash if the code is right, else raise."""
    ph = crypto.phone_hash(crypto.normalise_phone(phone))
    ch = (
        OtpChallenge.objects.select_for_update()
        .filter(phone_hash=ph, consumed_at__isnull=True, expires_at__gt=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if not ch:
        raise OtpError("OTP expired. Request a new one.")
    if ch.attempts >= MAX_ATTEMPTS:
        raise OtpError("Too many wrong attempts. Request a new OTP.")
    if not secrets.compare_digest(ch.code_hash, _hash(code.strip(), ph)):
        ch.attempts += 1
        ch.save(update_fields=["attempts"])
        raise OtpError("Incorrect OTP.")
    ch.consumed_at = timezone.now()
    ch.save(update_fields=["consumed_at"])
    return ph
