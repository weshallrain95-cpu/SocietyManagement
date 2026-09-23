"""Field-level encryption for PII (phones, owner contacts, key instructions) and HMAC lookups."""
import base64
import hashlib
import hmac
import os
import re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings

_NONCE = 12


def _key() -> bytes:
    key = base64.b64decode(settings.OB_FIELD_KEY)
    if len(key) != 32:
        raise ValueError("OB_FIELD_KEY must be 32 bytes, base64-encoded")
    return key


def encrypt(plaintext: str | None) -> bytes | None:
    if plaintext is None or plaintext == "":
        return None
    nonce = os.urandom(_NONCE)
    return nonce + AESGCM(_key()).encrypt(nonce, plaintext.encode(), None)


def decrypt(blob: bytes | memoryview | None) -> str | None:
    if not blob:
        return None
    blob = bytes(blob)
    return AESGCM(_key()).decrypt(blob[:_NONCE], blob[_NONCE:], None).decode()


def normalise_phone(raw: str) -> str:
    """Return E.164. Bare 10-digit numbers are assumed Indian (+91)."""
    digits = re.sub(r"[^\d+]", "", raw or "")
    if digits.startswith("+"):
        number = "+" + re.sub(r"\D", "", digits)
    else:
        digits = re.sub(r"\D", "", digits)
        if digits.startswith("0") and len(digits) == 11:
            digits = digits[1:]
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        if len(digits) != 10 or digits[0] not in "6789":
            raise ValueError("Enter a valid 10-digit Indian mobile number")
        number = "+91" + digits
    if not re.fullmatch(r"\+\d{8,15}", number):
        raise ValueError("Invalid phone number")
    return number


def phone_hash(e164: str) -> str:
    return hmac.new(settings.OB_PHONE_PEPPER.encode(), e164.encode(), hashlib.sha256).hexdigest()


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode()


def mask_phone(e164: str | None) -> str:
    if not e164:
        return ""
    return e164[:3] + " ••••• " + e164[-3:]
