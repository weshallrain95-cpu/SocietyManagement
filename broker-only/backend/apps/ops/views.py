"""Ops console (/ops/): the platform team's desk. Staff only; every action is audited.

Broker verification, the review queue (new societies, pin corrections, status conflicts,
reported enquiries), society pins and names, and tamper-evidence checks.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.audit.models import AuditEvent
from apps.audit.services import audit, verify_chain
from apps.masterdata import dedupe
from apps.masterdata.layout import expected_units, layout_dict
from apps.masterdata.models import Building, Society, SocietyAlias
from apps.masterdata.normalise import normalise_building, normalise_name
from apps.masterdata.services import (
    MasterDataError,
    approve_provisional,
    get_or_create_building,
    merge_societies,
    move_society_pin,
    parse_maps_link,
)
from apps.orgs.models import BrokerOrg
from apps.status.services import verify_ledger
from common.models import ReviewQueueItem
from common.rls import platform_context


def staff_only(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('ops-login')}?next={request.path}")
        if not request.user.is_staff:
            ctx = {"title": "Staff only", "body": "This area is for the Only Broker operations team."}
            return render(request, "ops/message.html", ctx, status=403)
        with platform_context():  # the ops team works across every broker firm; each action is audited
            resp = view(request, *args, **kwargs)
        resp["Cache-Control"] = "no-store"
        resp["X-Robots-Tag"] = "noindex, nofollow"
        return resp

    return inner


class Login(auth_views.LoginView):
    template_name = "ops/login.html"
    redirect_authenticated_user = True


def _counts():
    return {
        "pending_brokers": BrokerOrg.objects.filter(verification_status="pending").count(),
        "open_items": ReviewQueueItem.objects.filter(state="open").count(),
        "provisional": Society.objects.filter(status="provisional").count(),
    }


@staff_only
def dashboard(request):
    by_kind = ReviewQueueItem.objects.filter(state="open").values("kind").annotate(n=Count("id")).order_by("-n")
    return render(
        request,
        "ops/dashboard.html",
        {
            "counts": _counts(),
            "by_kind": by_kind,
            "brokers": BrokerOrg.objects.aggregate(total=Count("id"), verified=Count("id", filter=Q(verification_status="verified"))),
            "societies": Society.objects.filter(status="active").count(),
            "recent": AuditEvent.objects.order_by("-seq")[:8],
            "nav": "home",
        },
    )


# --- brokers ---------------------------------------------------------------------------------


@staff_only
def brokers(request):
    state = request.GET.get("state", "pending")
    qs = BrokerOrg.objects.filter(verification_status=state).annotate(members=Count("memberships")).order_by("created_at")
    return render(request, "ops/brokers.html", {"orgs": qs, "state": state, "counts": _counts(), "nav": "brokers"})


@staff_only
@require_POST
def broker_decide(request, pk):
    org = get_object_or_404(BrokerOrg, pk=pk)
    decision = request.POST.get("decision")
    if decision not in ("verified", "rejected", "suspended"):
        messages.error(request, "Choose verify, reject or suspend.")
        return redirect("ops-brokers")
    note = request.POST.get("note", "").strip()[:300]
    if decision != "verified" and not note:
        messages.error(request, "Add a short reason when rejecting or suspending — the broker is told why.")
        return redirect("ops-brokers")
    org.verification_status, org.verification_note = decision, note
    if decision == "verified" and request.POST.get("rera_verified") and org.rera_agent_no:
        org.rera_verified_at = timezone.now()
    org.save()
    audit(request.user, f"broker_org.{decision}", org, {"note": note, "via": "ops"})
    messages.success(request, f"{org.name}: {decision}.")
    return redirect("ops-brokers")


# --- review queue ------------------------------------------------------------------------------


@staff_only
def queue(request):
    kind = request.GET.get("kind", "")
    items = ReviewQueueItem.objects.filter(state="open").order_by("created_at")
    if kind:
        items = items.filter(kind=kind)
    rows = []
    for it in items[:100]:
        row = {"item": it, "society": None}
        if it.ref_type == "masterdata.society":
            row["society"] = Society.objects.select_related("locality").filter(pk=it.ref_id).first()
            if row["society"] is not None and it.kind == "provisional_society":
                row["candidates"] = [
                    c
                    for c in dedupe.find_candidates(row["society"].canonical_name, point=row["society"].location)
                    if c.society.pk != row["society"].pk
                ][:3]
        rows.append(row)
    kinds = ReviewQueueItem.objects.filter(state="open").values_list("kind", flat=True).distinct()
    return render(request, "ops/queue.html", {"rows": rows, "kind": kind, "kinds": sorted(set(kinds)), "counts": _counts(), "nav": "queue"})


@staff_only
@require_POST
def queue_act(request, pk):
    it = get_object_or_404(ReviewQueueItem, pk=pk, state="open")
    action = request.POST.get("action")
    try:
        if action == "approve" and it.ref_type == "masterdata.society":
            approve_provisional(Society.objects.get(pk=it.ref_id), user=request.user)
            outcome = "Society approved"
        elif action == "merge" and it.ref_type == "masterdata.society":
            src = Society.objects.get(pk=it.ref_id)
            dst = Society.objects.get(pk=request.POST.get("into"))
            r = merge_societies(src, dst, user=request.user)
            outcome = f"Merged into {dst.canonical_name} ({r['merged_units']} duplicate flats joined)"
        elif action == "reject" and it.ref_type == "masterdata.society":
            s = Society.objects.get(pk=it.ref_id)
            s.status = Society.Status.REJECTED
            s.save(update_fields=["status"])
            audit(request.user, "society.rejected", s)
            outcome = "Society rejected"
        elif action == "resolve":
            outcome = request.POST.get("note", "").strip() or "Resolved"
        else:
            messages.error(request, "That action does not apply to this item.")
            return redirect("ops-queue")
    except (MasterDataError, Society.DoesNotExist, ValidationError, ValueError) as e:
        messages.error(request, str(e) if isinstance(e, MasterDataError) else "Pick a society to merge into.")
        return redirect("ops-queue")
    it.state, it.resolved_by, it.resolved_at, it.resolution = "resolved", request.user, timezone.now(), outcome[:300]
    it.save()
    messages.success(request, outcome)
    return redirect("ops-queue")


# --- societies ---------------------------------------------------------------------------------


@staff_only
def societies(request):
    q = request.GET.get("q", "").strip()
    qs = Society.objects.select_related("locality").exclude(status__in=["merged", "rejected"])
    if q:
        qs = qs.annotate(sim=TrigramSimilarity("name_normalised", normalise_name(q).text)).filter(sim__gt=0.15).order_by("-sim")
    else:
        qs = qs.order_by("locality__name", "canonical_name")
    return render(request, "ops/societies.html", {"rows": qs[:200], "q": q, "counts": _counts(), "nav": "societies"})


@staff_only
def society(request, pk):
    s = get_object_or_404(Society.objects.select_related("locality"), pk=pk)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "pin":
            point = parse_maps_link(request.POST.get("link", ""))
            if point is None:
                messages.error(request, "Couldn’t read a location. Paste a full Google Maps link with coordinates, or “19.2601, 72.9663”.")
            else:
                r = move_society_pin(s, point, user=request.user, reason=request.POST.get("reason", "ops edit"))
                messages.success(request, f"Pin moved; distances recalculated ({r['buildings_moved']} buildings moved with it).")
        elif action == "layout":
            b = get_object_or_404(Building, pk=request.POST.get("building_id"), society=s)
            try:
                _save_layout(b, request.POST, user=request.user)
                messages.success(request, f"{b.name}: layout saved.")
            except ValueError as e:
                messages.error(request, f"{b.name}: {e}")
        elif action == "add_wing" and request.POST.get("wing", "").strip():
            name = request.POST["wing"].strip()[:80]
            if s.buildings.filter(name_normalised=normalise_building(name), merged_into__isnull=True).exists():
                messages.error(request, f"{name} already exists.")
            else:
                b = get_or_create_building(s, name)
                audit(request.user, "building.added", b, {"society": str(s.pk)})
                messages.success(request, f"Wing {name} added. Now fill in its floors.")
        elif action == "wings_complete":
            s.wings_complete = request.POST.get("value") == "1"
            s.save(update_fields=["wings_complete"])
            audit(request.user, "society.wings_complete", s, {"value": s.wings_complete})
            messages.success(request, "Brokers can no longer add wings here." if s.wings_complete else "Brokers may add new wings again.")
        elif action == "add_alias" and request.POST.get("alias", "").strip():
            dedupe.learn_alias(s, request.POST["alias"].strip(), SocietyAlias.Source.ADMIN)
            audit(request.user, "society.alias_added", s, {"alias": request.POST["alias"].strip()[:120]})
            messages.success(request, "Name added — uploads using it will now match this society.")
        elif action == "remove_alias":
            a = SocietyAlias.objects.filter(pk=request.POST.get("alias_id"), society=s).first()
            if a:
                audit(request.user, "society.alias_removed", s, {"alias": a.alias_raw})
                a.delete()
                messages.success(request, "Name removed.")
        return redirect("ops-society", pk=s.pk)
    buildings = list(
        s.buildings.filter(merged_into__isnull=True).annotate(n_units=Count("units")).prefetch_related("location_facts").order_by("name")
    )
    for b in buildings:
        b.expected = expected_units(b)
    return render(
        request,
        "ops/society.html",
        {
            "s": s,
            "aliases": s.aliases.order_by("-confirmations"),
            "counts": _counts(),
            "nav": "societies",
            "buildings": buildings,
            "sources": LAYOUT_SOURCES,
            "gmaps": f"https://www.google.com/maps/search/?api=1&query={s.location.y},{s.location.x}",
        },
    )


@staff_only
def pin_map(request):
    """Every society pin on one map: green active, amber waiting for review."""
    pins = [
        {
            "id": str(s.pk),
            "name": s.canonical_name,
            "locality": s.locality.name,
            "status": s.status,
            "lat": round(s.location.y, 6),
            "lng": round(s.location.x, 6),
            "url": reverse("ops-society", args=[s.pk]),
        }
        for s in Society.objects.select_related("locality").filter(status__in=["active", "provisional"])
    ]
    return render(request, "ops/map.html", {"pins": pins, "counts": _counts(), "nav": "map"})


LAYOUT_SOURCES = ["rera", "survey", "ops", "broker"]


def _int_list(text: str) -> list[int]:
    try:
        return sorted({int(x) for x in text.replace(";", ",").split(",") if x.strip()})
    except ValueError:
        raise ValueError("floors with no flats must be numbers, e.g. 11, 22") from None


def _opt_int(v: str, label: str, lo: int, hi: int):
    if not (v or "").strip():
        return None
    if not v.strip().lstrip("-").isdigit() or not lo <= int(v) <= hi:
        raise ValueError(f"{label} must be a number from {lo} to {hi}")
    return int(v)


def _save_layout(b: Building, post, *, user) -> None:
    before = layout_dict(b)
    b.floors_total = _opt_int(post.get("floors_total", ""), "Floors", 0, 120)
    lowest = _opt_int(post.get("lowest_floor", ""), "First floor with flats", 0, 10)
    b.lowest_floor = 1 if lowest is None else lowest
    b.units_per_floor = _opt_int(post.get("units_per_floor", ""), "Flats per floor", 1, 40)
    b.skip_floors = _int_list(post.get("skip_floors", ""))
    b.extra_unit_nos = [x.strip()[:30] for x in post.get("extra_unit_nos", "").split(",") if x.strip()]
    b.layout_source = post.get("layout_source", "") if post.get("layout_source") in LAYOUT_SOURCES else "ops"
    b.layout_verified = post.get("layout_verified") == "1"
    if b.layout_verified and not (b.floors_total and b.units_per_floor):
        raise ValueError("fill in floors and flats per floor before marking the layout verified")
    b.save()
    audit(user, "building.layout_changed", b, {"from": before, "to": layout_dict(b)})


# --- audit -------------------------------------------------------------------------------------------


@staff_only
def audit_view(request):
    return render(
        request,
        "ops/audit.html",
        {
            "audit": verify_chain(),
            "ledger": verify_ledger(),
            "events": AuditEvent.objects.order_by("-seq")[:100],
            "counts": _counts(),
            "nav": "audit",
        },
    )
