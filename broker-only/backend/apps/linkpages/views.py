"""Pages opened from WhatsApp/SMS links by owners and offline customers (PRD OFF-*, STAT-05, VISIT-05, REV).

No app, no login: the token in the address is the permission. Pages are server-rendered, work
without JavaScript and stay small for slow connections. Each page shows only what that person
is entitled to see.
"""

from datetime import date, datetime
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.crm import services as crm
from apps.reviews import services as reviews
from apps.reviews.models import Interaction
from apps.status import services as status_svc
from apps.status.models import StatusConfirmation
from apps.visits import services as visits
from apps.visits.models import VisitStop
from common import rls
from common.links import LinkError, resolve_link
from common.models import ShareLink

RATE = 30  # requests per minute per IP


def guarded(view):
    """Rate-limit, and turn invalid/expired/used links into a friendly page."""

    @wraps(view)
    def inner(request, token, *args, **kwargs):
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
        key = f"linkpage:{ip}:{timezone.now():%Y%m%d%H%M}"
        hits = cache.get_or_set(key, 0, 70)
        if hits >= RATE:
            return page(
                request,
                "linkpages/message.html",
                {"title": "Please wait a minute", "body": "Too many attempts from this connection."},
                status=429,
            )
        cache.incr(key)
        try:
            resp = view(request, token, *args, **kwargs)
        except LinkError as e:
            return page(
                request,
                "linkpages/message.html",
                {"title": "This link can’t be used", "body": str(e) + " Ask your broker to send a new one."},
                status=410,
            )
        return resp

    return inner


def page(request, template, ctx, status=200) -> HttpResponse:
    resp = render(request, template, ctx, status=status)
    # "same-origin": the private link is never sent to other sites (maps, etc.), while our own
    # forms keep a real Origin header. ("no-referrer" makes browsers send Origin: null and
    # Django's CSRF check then rejects every button press.)
    resp["Referrer-Policy"] = "same-origin"
    resp["X-Robots-Tag"] = "noindex, nofollow"
    resp["Cache-Control"] = "no-store"
    return resp


def _org_name(org_id) -> str:
    from apps.orgs.models import BrokerOrg

    return BrokerOrg.objects.filter(pk=org_id).values_list("name", flat=True).first() or "Your broker"


def _flat_label(unit) -> str:
    return f"Flat {unit.unit_no}, {unit.building.name}, {unit.building.society.canonical_name}"


# --- owner: is the flat available? (STAT-05) ------------------------------------------------


@require_http_methods(["GET", "POST"])
@guarded
def confirm_status(request, token):
    link = _peek(token, ShareLink.Purpose.STATUS_CONFIRMATION)  # an answered link still shows its thank-you
    conf = StatusConfirmation.objects.select_related("unit__building__society", "requested_by_org").get(pk=link.target_id)
    ctx = {
        "broker": conf.requested_by_org.name if conf.requested_by_org else "A broker",
        "flat": _flat_label(conf.unit),
        "noun": "rent" if conf.txn_type == "RENT" else "sale",
        "answered": conf.response,
        "today": timezone.localdate().isoformat(),
    }
    if request.method == "POST" and not conf.response:
        answer = request.POST.get("answer")
        when = None
        if answer == "available_from":
            try:
                when = date.fromisoformat(request.POST.get("available_from", ""))
            except ValueError:
                ctx["error"] = "Please choose the date it will be available."
                return page(request, "linkpages/confirm_status.html", ctx, status=400)
        if answer not in ("yes", "no", "available_from"):
            ctx["error"] = "Please choose one of the options."
            return page(request, "linkpages/confirm_status.html", ctx, status=400)
        resolve_link(token, ShareLink.Purpose.STATUS_CONFIRMATION, consume=True)
        status_svc.owner_responds(conf, answer, available_from=when)
        return redirect(request.path)
    return page(request, "linkpages/confirm_status.html", ctx)


# --- owner: a visit is scheduled at your flat (VISIT-05) -----------------------------------


@require_http_methods(["GET", "POST"])
@guarded
def visit_notice(request, token):
    link = (
        resolve_link(token, ShareLink.Purpose.VISIT_NOTICE, consume=False)
        if request.method == "POST"
        else _peek(token, ShareLink.Purpose.VISIT_NOTICE)
    )
    with rls.platform_context():
        stop = VisitStop.objects.select_related("listing__unit__building__society", "plan").get(pk=link.target_id)
        ctx = {
            "broker": _org_name(stop.org_id),
            "flat": _flat_label(stop.listing.unit),
            "when": stop.slot_start,
            "day": stop.plan.date,
            "state": stop.owner_notice,
        }
    if request.method == "POST" and stop.owner_notice == VisitStop.OwnerNotice.SENT:
        visits.owner_acknowledges(token, request.POST.get("answer") == "ok")
        return redirect(request.path)
    return page(request, "linkpages/visit_notice.html", ctx)


def _peek(token, purpose):
    """Read a single-use link without spending it; a used link may still be viewed to show its outcome."""
    from common.crypto import token_hash

    link = ShareLink.objects.filter(token_hash=token_hash(token), purpose=purpose, revoked_at__isnull=True).first()
    if not link or link.expires_at < timezone.now():
        raise LinkError("This link is not valid or has expired.")
    return link


# --- customer: shortlist from the broker (OFF-03) -------------------------------------------


@require_http_methods(["GET", "POST"])
@guarded
def shortlist(request, token):
    if request.method == "POST":
        crm.respond_to_shortlist_item(token, request.POST.get("item"), request.POST.get("response", ""))
        return redirect(f"{request.path}?r=1#item-{request.POST.get('item')}")
    data = crm.public_shortlist(token, log_open=not request.GET.get("r"))
    for it in data["items"]:
        it["facts"] = _facts(it["location_facts"])
        it["highlights"] = _highlights(it["attributes"])
    return page(request, "linkpages/shortlist.html", data)


FACT_LABEL = {
    "rail_station": "station",
    "metro_station": "metro",
    "auto_stand": "auto stand",
    "school": "school",
    "bus_stop": "bus stop",
    "hospital": "hospital",
    "market": "market",
}


def _facts(facts: dict) -> list[str]:
    out = []
    for key in ("rail_station", "metro_station", "auto_stand", "school", "bus_stop", "market", "hospital"):
        f = facts.get(key)
        if not f:
            continue
        dist = f"{f['distance_m'] / 1000:.1f} km" if f["distance_m"] >= 1000 else f"{f['distance_m']} m"
        how = f"{f['walk_min']} min walk" if f["walk_min"] <= 15 else f"{f['drive_min']} min by auto"
        kind = FACT_LABEL[key]
        name = f["name"] if kind.split()[-1] in f["name"].lower() else f"{f['name']} {kind}"
        out.append(f"{name}: {dist} · {how}")
    return out[:4]


def _highlights(attrs: dict) -> list[str]:
    out = []
    for a in attrs.values():
        v = a["value"]
        if v is True:
            out.append(a["label"])
        elif isinstance(v, str) and v not in ("no", "not allowed", "none"):
            out.append(f"{a['label']}: {v}")
    return out[:6]


# --- customer: visit plan (OFF-04, VISIT-02) --------------------------------------------------


@require_http_methods(["GET", "POST"])
@guarded
def visit_plan(request, token):
    if request.method == "POST":
        slot = None
        if request.POST.get("action") == "propose":
            try:
                slot = timezone.make_aware(datetime.fromisoformat(request.POST.get("slot", "")))
            except ValueError:
                data = visits.public_plan_view(token)
                data["broker"] = _org_name(data.pop("org_id"))
                data["day"] = date.fromisoformat(data["date"])
                data["error"] = "Please choose a date and time."
                return page(request, "linkpages/visit_plan.html", data, status=400)
        visits.customer_confirms(token, slot=slot)
        return redirect(f"{request.path}?done={'proposed' if slot else 'confirmed'}")
    data = visits.public_plan_view(token)
    data["broker"] = _org_name(data.pop("org_id"))
    for s in data["stops"]:
        s["slot_start"] = datetime.fromisoformat(s["slot_start"]) if s["slot_start"] else None
    data["day"] = date.fromisoformat(data["date"])
    data["done"] = request.GET.get("done")
    data["confirmed"] = data["state"] in ("customer_confirmed", "in_progress", "completed")
    return page(request, "linkpages/visit_plan.html", data)


# --- customer: consent (OFF-02) -----------------------------------------------------------------


@require_http_methods(["GET", "POST"])
@guarded
def consent(request, token):
    if request.method == "POST":
        c = crm.confirm_consent_link(token, agree=request.POST.get("answer") == "agree")
        return page(
            request,
            "linkpages/message.html",
            {
                "title": "Thank you" if c.consent_state == "link_confirmed" else "Noted",
                "body": "Your broker can now send you flat details and visit plans on WhatsApp/SMS."
                if c.consent_state == "link_confirmed"
                else "You will not receive messages. You can still call your broker.",
            },
        )
    link = resolve_link(token, ShareLink.Purpose.CONSENT, consume=False)
    from apps.crm.models import Customer

    with rls.platform_context():
        broker = _org_name(Customer.objects.values_list("org_id", flat=True).get(pk=link.target_id))
    return page(request, "linkpages/consent.html", {"broker": broker})


# --- customer: review the broker after a visit (REV-01, OFF-08) -----------------------------


@require_http_methods(["GET", "POST"])
@guarded
def review(request, token):
    link = resolve_link(token, ShareLink.Purpose.REVIEW, consume=False)
    inter = Interaction.objects.get(pk=link.target_id)
    ctx = {
        "broker": _org_name(inter.org_id),
        "tags": [(t, t.replace("_", " ").capitalize()) for t in sorted(reviews.ALLOWED_TAGS)],
        "stars_range": range(5, 0, -1),
    }
    if request.method == "POST":
        try:
            reviews.review_via_link(
                token, stars=int(request.POST.get("stars", 0)), tags=request.POST.getlist("tags"), text=request.POST.get("text", "")
            )
        except (ValueError, reviews.ReviewError):
            ctx["error"] = "Please choose 1 to 5 stars."
            return page(request, "linkpages/review.html", ctx, status=400)
        return page(
            request,
            "linkpages/message.html",
            {"title": "Thank you!", "body": f"Your review helps other families choose a good broker. {ctx['broker']} will see it."},
        )
    return page(request, "linkpages/review.html", ctx)
