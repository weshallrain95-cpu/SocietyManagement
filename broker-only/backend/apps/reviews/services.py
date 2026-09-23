"""360° reviews (REV-01..05). Reviews exist only on top of a verified interaction."""

from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count
from django.utils import timezone

from apps.orgs.models import BrokerOrg
from common.links import create_link, resolve_link
from common.models import ShareLink
from common.notify import send_message

from .models import Interaction, Review

PRIOR_MEAN = Decimal("4.0")
PRIOR_WEIGHT = 5
EDIT_WINDOW_DAYS = 7
ALLOWED_TAGS = {
    "punctual",
    "honest_listing",
    "knowledgeable",
    "responsive",
    "patient",
    "good_negotiator",
    "well_organised_visits",
    "respectful",
    "clear_terms",
}


class ReviewError(Exception):
    pass


def visit_completed(plan) -> Interaction:
    customer = plan.customer
    inter, created = Interaction.objects.get_or_create(
        kind=Interaction.Kind.VISIT_COMPLETED,
        ref_type="visits.visitplan",
        ref_id=plan.pk,
        defaults={
            "org_id": plan.org_id,
            "customer_user": customer.platform_user,
            "customer_phone_hash": customer.phone_hash,
            "occurred_at": timezone.now(),
        },
    )
    if created and customer.can_message:
        _, token = create_link(ShareLink.Purpose.REVIEW, inter, hours=24 * 14, recipient_phone_hash=customer.phone_hash)
        send_message(customer.phone, "review_request", {"url": f"{settings.OB_PUBLIC_BASE_URL}/r/{token}"}, phone_hash=customer.phone_hash)
    return inter


def _clean(stars, tags, text):
    if not 1 <= int(stars) <= 5:
        raise ReviewError("Stars must be 1 to 5")
    bad = set(tags) - ALLOWED_TAGS
    if bad:
        raise ReviewError(f"Unknown tags: {sorted(bad)}")
    return int(stars), sorted(set(tags)), (text or "")[:1000]


@transaction.atomic
def review_via_link(token: str, *, stars, tags=(), text="") -> Review:
    """OFF-08: offline customers review through a one-time link; labelled 'verified visit'."""
    link = resolve_link(token, ShareLink.Purpose.REVIEW, consume=True)
    inter = Interaction.objects.get(pk=link.target_id)
    stars, tags, text = _clean(stars, tags, text)
    try:
        with transaction.atomic():
            r = Review.objects.create(
                interaction=inter,
                direction=Review.Direction.C2B,
                reviewer_user=inter.customer_user,
                reviewer_label="Verified visit",
                org_id=inter.org_id,
                stars=stars,
                tags=tags,
                text=text,
                verified_offline=inter.customer_user is None,
            )
    except IntegrityError as e:
        raise ReviewError("This visit has already been reviewed") from e
    recompute_reputation(inter.org_id)
    return r


@transaction.atomic
def submit(interaction: Interaction, *, reviewer, direction: str, stars, tags=(), text="") -> Review:
    """In-app reviews: customer->broker (C2B) and broker->customer (B2C) in MVP."""
    stars, tags, text = _clean(stars, tags, text)
    if direction == Review.Direction.C2B:
        if interaction.customer_user_id != reviewer.pk:
            raise ReviewError("Only the customer of this visit can review the broker")
        kw = {"org_id": interaction.org_id}
    elif direction == Review.Direction.B2C:
        if not reviewer.memberships.filter(org_id=interaction.org_id, active=True).exists():
            raise ReviewError("Only the broker of this visit can review the customer")
        if interaction.customer_user_id is None:
            raise ReviewError("This customer is not on the platform")
        kw = {"reviewee_user_id": interaction.customer_user_id}
    else:
        raise ReviewError("Direction not available yet")
    try:
        with transaction.atomic():
            r = Review.objects.create(
                interaction=interaction, direction=direction, reviewer_user=reviewer, stars=stars, tags=tags, text=text, **kw
            )
    except IntegrityError as e:
        raise ReviewError("Already reviewed") from e
    if direction == Review.Direction.C2B:
        recompute_reputation(interaction.org_id)
    return r


def recompute_reputation(org_id) -> None:
    """REV-03: Bayesian average so one 5-star review does not beat fifty 4.6s."""
    agg = Review.objects.filter(org_id=org_id, direction="C2B", moderation_state="published").aggregate(n=Count("id"), avg=Avg("stars"))
    n = agg["n"] or 0
    avg = Decimal(str(agg["avg"] or 0))
    bayes = (PRIOR_MEAN * PRIOR_WEIGHT + avg * n) / (PRIOR_WEIGHT + n)
    BrokerOrg.objects.filter(pk=org_id).update(rating_bayes=round(bayes, 2), rating_count=n)
