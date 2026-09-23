"""Create and redeem tokenised share links."""
from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .crypto import new_token, token_hash
from .models import ShareLink


class LinkError(Exception):
    pass


def create_link(purpose, target, *, hours=72, max_uses=1, recipient_phone_hash="", data=None) -> tuple[ShareLink, str]:
    token = new_token()
    link = ShareLink.objects.create(
        purpose=purpose,
        token_hash=token_hash(token),
        target_type=target._meta.label_lower,
        target_id=target.pk,
        recipient_phone_hash=recipient_phone_hash,
        expires_at=timezone.now() + timedelta(hours=hours),
        max_uses=max_uses,
        data=data or {},
    )
    return link, token


def resolve_link(token: str, purpose: str, *, consume: bool) -> ShareLink:
    with transaction.atomic():
        link = ShareLink.objects.select_for_update().filter(token_hash=token_hash(token), purpose=purpose).first()
        if not link or link.revoked_at:
            raise LinkError("This link is not valid.")
        if link.expires_at < timezone.now():
            raise LinkError("This link has expired.")
        if link.uses >= link.max_uses:
            raise LinkError("This link has already been used.")
        if consume:
            ShareLink.objects.filter(pk=link.pk).update(uses=F("uses") + 1)
            link.uses += 1
        return link
