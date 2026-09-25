"""The broker's flat list at scale (1,000+ flats): one search box, filters, quick views, sorting, and
browsing by society and wing.

The search box takes whatever the broker has in mind: "HE A-1203", "rodas 12", "Amara 1501", the owner's
name ("Kulkarni") or the owner's number ("98190 12345"). Only the broker's own flats are searched (RLS);
nothing here ever shows another firm's inventory.
"""

import re
from datetime import timedelta

from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone

from apps.owners.models import UnitMedia
from apps.status.models import UnitStatus
from common import crypto

from .models import KeyCustody
from .search import search_flats

STALE_DAYS = {"RENT": 21}
DEFAULT_STALE = 45
SORTS = {
    "confirmed": ("-last_confirmed_at",),
    "newest": ("-created_at",),
    "price_low": ("_price", "-last_confirmed_at"),
    "price_high": ("-_price", "-last_confirmed_at"),
}
QUICK = ("reconfirm", "new", "keys_office", "no_photos")


def _phone_query(q: str) -> str | None:
    digits = re.sub(r"\D", "", q)
    if len(digits) < 10 or re.search(r"[a-zA-Z]", q):
        return None
    try:
        return crypto.phone_hash(crypto.normalise_phone(digits[-10:]))
    except ValueError:
        return None


def text_filter(qs, q: str, *, org):
    """Society / wing / flat number (fuzzy, nicknames), owner name, or owner phone."""
    q = (q or "").strip()[:100]
    if not q:
        return qs
    ph = _phone_query(q)
    if ph:
        return qs.filter(owner_phone_hash=ph)
    ids = {l.pk for l in search_flats(qs, q, org=org, limit=1000)["results"]}
    name_hits = qs.filter(owner_name__icontains=q).values_list("pk", flat=True) if len(q) >= 3 else []
    return qs.filter(Q(pk__in=ids) | Q(pk__in=list(name_hits)))


def _stale_q(now):
    return Q(txn_type="RENT", last_confirmed_at__lt=now - timedelta(days=STALE_DAYS["RENT"])) | (
        ~Q(txn_type="RENT") & Q(last_confirmed_at__lt=now - timedelta(days=DEFAULT_STALE))
    )


def available_now_q():
    """The broker's "Available now" list: flats they turned on that are still on offer or on hold."""
    from .services import AVAILABLE_NOW_STATES

    live = UnitStatus.objects.filter(unit=OuterRef("unit"), txn_type=OuterRef("txn_type"), state__in=AVAILABLE_NOW_STATES)
    return Q(available_now=True) & Exists(live)


def _annotate(qs):
    live_photo = UnitMedia.objects.filter(unit=OuterRef("unit"), kind="photo", state="live", deleted_at__isnull=True)
    office_keys = KeyCustody.objects.filter(listing=OuterRef("pk"), to_ts__isnull=True, holder_type="office")
    return qs.annotate(_has_photo=Exists(live_photo), _keys_office=Exists(office_keys))


def quick_q(name: str, now):
    return {
        # Only flats the broker is offering need reconfirming; a rented-out or parked flat does not.
        "reconfirm": _stale_q(now) & available_now_q(),
        "new": Q(created_at__gte=now - timedelta(days=7)),
        "keys_office": Q(_keys_office=True),
        "no_photos": Q(_has_photo=False),
    }[name]


def browse(base, params, *, org):
    """Returns (page of listings, total matching, quick-view counts over the unfiltered base)."""
    now = timezone.now()
    base = _annotate(base.filter(archived_at__isnull=True).select_related("unit__building__society__locality"))
    counts = {
        "total": base.count(),
        "available_now": base.filter(available_now_q()).count(),
        **{k: base.filter(quick_q(k, now)).count() for k in QUICK},
    }

    qs = text_filter(base, params.get("q", ""), org=org)
    if params.get("list") == "available_now":
        qs = qs.filter(available_now_q())
    if params.get("txn_type"):
        qs = qs.filter(txn_type__in=params["txn_type"].split(","))
    if params.get("status"):
        states = params["status"].split(",")
        sub = UnitStatus.objects.filter(unit=OuterRef("unit"), txn_type=OuterRef("txn_type"), state__in=states)
        qs = qs.filter(Exists(sub))
    if params.get("bhk"):
        wanted = [float(x) for x in params["bhk"].split(",") if re.fullmatch(r"\d+(\.\d)?", x)]
        cond = Q()
        for b in wanted:
            cond |= Q(unit__bhk__gte=4) if b >= 4 else Q(unit__bhk=b)
        qs = qs.filter(cond) if wanted else qs
    lo, hi = params.get("price_min"), params.get("price_max")
    if lo or hi:
        price = Q()
        if lo and str(lo).isdigit():
            price &= Q(asking_rent__gte=int(lo)) | Q(asking_price__gte=int(lo))
        if hi and str(hi).isdigit():
            price &= Q(asking_rent__lte=int(hi), txn_type="RENT") | (Q(asking_price__lte=int(hi)) & ~Q(txn_type="RENT"))
        qs = qs.filter(price)
    if params.get("locality_id"):
        qs = qs.filter(unit__building__society__locality_id=params["locality_id"])
    if params.get("society_id"):
        qs = qs.filter(unit__building__society_id=params["society_id"])
    if params.get("building_id"):
        qs = qs.filter(unit__building_id=params["building_id"])
    if params.get("quick") in QUICK:
        qs = qs.filter(quick_q(params["quick"], now))

    sort = SORTS.get(params.get("sort") or "confirmed", SORTS["confirmed"])
    if any("_price" in s for s in sort):
        from django.db.models import BigIntegerField
        from django.db.models.functions import Coalesce

        qs = qs.annotate(_price=Coalesce("asking_rent", "asking_price", output_field=BigIntegerField()))
    qs = qs.order_by(*sort, "pk")
    total = qs.count()
    try:
        offset = max(0, int(params.get("offset", 0)))
        limit = min(100, max(1, int(params.get("limit", 50))))
    except ValueError:
        offset, limit = 0, 50
    return list(qs[offset : offset + limit]), total, counts


def by_society(base):
    """Society → wing → number of the broker's open flats, biggest first."""
    rows = (
        base.filter(archived_at__isnull=True)
        .values("unit__building__society_id", "unit__building__society__canonical_name", "unit__building_id", "unit__building__name")
        .annotate(n=Count("id"))
    )
    socs: dict = {}
    for r in rows:
        s = socs.setdefault(
            r["unit__building__society_id"],
            {
                "society_id": str(r["unit__building__society_id"]),
                "name": r["unit__building__society__canonical_name"],
                "count": 0,
                "wings": [],
            },
        )
        s["count"] += r["n"]
        s["wings"].append({"building_id": str(r["unit__building_id"]), "name": r["unit__building__name"], "count": r["n"]})
    out = sorted(socs.values(), key=lambda s: (-s["count"], s["name"]))
    for s in out:
        s["wings"].sort(key=lambda w: (-w["count"], w["name"]))
    return out
