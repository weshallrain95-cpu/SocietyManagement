"""Broadcast API: brokers write to their own customers; customers read and mute updates."""

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.inventory.models import Listing
from apps.masterdata.models import Locality
from apps.orgs.permissions import IsBrokerManager
from common.api import domain_call

from . import broadcasts as bc
from .models import Broadcast


def _target(request):
    listing = (
        get_object_or_404(Listing, pk=request.data.get("listing_id") or request.query_params.get("listing_id"))
        if (request.data.get("listing_id") or request.query_params.get("listing_id"))
        else None
    )
    loc_id = request.data.get("locality_id") or request.query_params.get("locality_id")
    locality = get_object_or_404(Locality, pk=loc_id) if loc_id else None
    return listing, locality


def _listings(request) -> list:
    raw = request.data.get("listing_ids") if hasattr(request.data, "get") else None
    raw = raw or request.query_params.get("listing_ids") or []
    ids = [x for x in (raw.split(",") if isinstance(raw, str) else raw) if x]
    if not ids:
        return []
    found = list(Listing.objects.filter(pk__in=ids).select_related("unit__building__society__locality"))  # RLS: own firm only
    if len(found) != len(set(ids)):
        raise Http404
    order = {str(x): i for i, x in enumerate(ids)}
    return sorted(found, key=lambda li: order[str(li.pk)])


def broadcast_json(b: Broadcast) -> dict:
    return {
        "id": str(b.pk),
        "kind": b.kind,
        "text": b.text,
        "listing_id": str(b.listing_id) if b.listing_id else None,
        "listing_ids": b.audience.get("listing_ids") or ([str(b.listing_id)] if b.listing_id else []),
        "locality": b.locality.name if b.locality_id else None,
        "audience": b.audience,
        "recipients_total": b.recipients_total,
        "delivered_in_app": b.delivered_in_app,
        "not_on_app": b.not_on_app,
        "muted": b.muted,
        "created_at": b.created_at.isoformat(),
    }


class BroadcastPreview(APIView):
    """GET ?kind=&listing_id=&locality_id=&scope= → suggested text and who it will reach."""

    permission_classes = [IsBrokerManager]

    def get(self, request):
        org = request.user.active_membership.org
        listing, locality = _target(request)
        listings = _listings(request) or ([listing] if listing else [])
        kind = request.query_params.get("kind", "news")
        scope = request.query_params.get("scope", "all")
        return Response(
            {
                "text": bc.default_text(kind, org=org, listing=listing, locality=locality, listings=listings),
                "flat": bc.flat_summary(listings[0]) if listings else None,
                "flats": [bc.flat_summary(li) for li in listings],
                "reach": bc.counts(bc.audience(org, scope=scope, locality=locality)),
                "free_in_pilot": True,
            }
        )


class BroadcastListCreate(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request):
        return Response([broadcast_json(b) for b in Broadcast.objects.select_related("locality").order_by("-created_at")[:50]])

    def post(self, request):
        org = request.user.active_membership.org
        listing, locality = _target(request)
        b, offline = domain_call(
            bc.send,
            org,
            user=request.user,
            kind=request.data.get("kind", ""),
            text=request.data.get("text", ""),
            listing=listing,
            listings=_listings(request),
            locality=locality,
            scope=request.data.get("scope", "all"),
        )
        return Response({**broadcast_json(b), "invite": offline}, status=201)


class MyUpdates(APIView):
    """The customer's inbox of broker updates."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(bc.my_updates(request.user))

    def post(self, request):
        return Response({"marked_read": bc.mark_read(request.user)})


class MuteBroker(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        muted = request.data.get("muted")
        if not isinstance(muted, bool) or not request.data.get("org_id"):
            return Response({"detail": "org_id and muted (true/false) are required"}, status=400)
        return Response({"updated": bc.set_muted(request.user, request.data["org_id"], muted)})
