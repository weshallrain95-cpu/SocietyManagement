from datetime import datetime

from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.crm.models import Customer
from apps.identity.models import User
from apps.inventory.models import Listing
from apps.orgs.permissions import IsBrokerManager, IsBrokerMember
from common.api import PublicLinkMixin, domain_call, is_field_staff

from . import services as v
from .models import VisitPlan, VisitStop


def plan_json(p: VisitPlan, request=None):
    stops = []
    for s in v.live_stops(p):
        b = s.listing.unit.building
        stops.append(
            {
                "id": str(s.id),
                "seq": s.seq,
                "listing_id": str(s.listing_id),
                "society": b.society.canonical_name,
                "building": b.name,
                "unit_no": s.listing.unit.unit_no,
                "slot_start": s.slot_start,
                "slot_end": s.slot_end,
                "location": {"lat": b.location.y, "lng": b.location.x},
                "navigate_url": f"https://www.google.com/maps/dir/?api=1&destination={b.location.y},{b.location.x}",
                "assigned_staff_id": str(s.assigned_staff_id) if s.assigned_staff_id else None,
                "staff_ack_at": s.staff_ack_at,
                "owner_notice": s.owner_notice,
                "checkin_at": s.checkin_at,
                "outcome": s.outcome,
            }
        )
    return {
        "id": str(p.id),
        "customer_id": str(p.customer_id),
        "customer_name": p.customer.name,
        "date": p.date,
        "start_time": p.start_time,
        "travel_mode": p.travel_mode,
        "state": p.state,
        "version": p.version,
        "total_travel_min": p.total_travel_min,
        "customer_proposed_slot": p.customer_proposed_slot,
        "stops": stops,
    }


def _plans(request):
    qs = VisitPlan.objects.select_related("customer")
    if is_field_staff(request):
        qs = qs.filter(stops__assigned_staff=request.user, stops__removed=False).distinct()
    return qs


class PlanSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    listing_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1, max_length=25)
    date = serializers.DateField()
    start_time = serializers.TimeField()
    start = serializers.DictField(required=False)
    travel_mode = serializers.ChoiceField(choices=VisitPlan.Mode.choices, default="two_wheeler")
    dwell_min = serializers.IntegerField(default=15, min_value=5, max_value=90)
    requirement_id = serializers.UUIDField(required=False)


class PlanListCreate(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        qs = _plans(request).order_by("date", "start_time")
        if request.query_params.get("date"):
            qs = qs.filter(date=request.query_params["date"])
        return Response([plan_json(p) for p in qs[:200]])

    def post(self, request):
        if not request.user.active_membership.can_manage:
            return Response(status=403)
        s = PlanSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        customer = get_object_or_404(Customer, pk=d["customer_id"])
        by_id = {l.pk: l for l in Listing.objects.filter(pk__in=d["listing_ids"]).select_related("unit__building")}
        listings = [by_id[i] for i in d["listing_ids"] if i in by_id]
        start = Point(float(d["start"]["lng"]), float(d["start"]["lat"]), srid=4326) if d.get("start") else None
        p = domain_call(
            v.create_plan,
            customer=customer,
            listings=listings,
            date=d["date"],
            start_time=d["start_time"],
            user=request.user,
            start_point=start,
            travel_mode=d["travel_mode"],
            dwell_min=d["dwell_min"],
        )
        return Response({**plan_json(p), "key_warnings": v.key_conflicts(p)}, status=201)


class PlanDetail(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request, pk):
        p = get_object_or_404(_plans(request), pk=pk)
        return Response({**plan_json(p), "key_warnings": v.key_conflicts(p)})


class PlanAction(APIView):
    """POST /visit-plans/<id>/<action>: optimise | share | assign | notify-owners | add-stop | reorder | cancel | ack"""

    permission_classes = [IsBrokerMember]

    def post(self, request, pk, action):
        p = get_object_or_404(_plans(request), pk=pk)
        if action == "ack":
            return Response({"acknowledged": v.acknowledge(p, request.user)})
        if not request.user.active_membership.can_manage:
            return Response(status=403)
        if action == "optimise":
            v.optimise_route(p)
        elif action == "share":
            domain_call(v.share_with_customer, p, user=request.user)
        elif action == "assign":
            staff = get_object_or_404(User, pk=request.data.get("staff_user_id"))
            domain_call(v.assign, p, staff, stop_ids=request.data.get("stop_ids"))
        elif action == "notify-owners":
            return Response({"notified": v.notify_owners(p)})
        elif action == "add-stop":
            listing = get_object_or_404(Listing, pk=request.data.get("listing_id"))
            domain_call(v.add_stop, p, listing, position=request.data.get("position"))
        elif action == "reorder":
            domain_call(v.reorder, p, request.data.get("stop_ids", []))
        elif action == "cancel":
            p.state = VisitPlan.State.CANCELLED
            p.save(update_fields=["state"])
        else:
            return Response({"detail": "Unknown action"}, status=404)
        p.refresh_from_db()
        return Response(plan_json(p))


class StopRemove(APIView):
    permission_classes = [IsBrokerManager]

    def delete(self, request, pk, stop_id):
        p = get_object_or_404(VisitPlan, pk=pk)
        v.remove_stop(p, get_object_or_404(VisitStop, pk=stop_id, plan=p))
        return Response(plan_json(p))


class StopCheckin(APIView):
    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        s = get_object_or_404(VisitStop, pk=pk, removed=False)
        if is_field_staff(request) and s.assigned_staff_id != request.user.pk:
            return Response(status=403)
        s = v.check_in(s, lat=request.data.get("lat"), lng=request.data.get("lng"))
        far = s.checkin_distance_m is not None and s.checkin_distance_m > v.CHECKIN_RADIUS_M
        return Response({"checkin_at": s.checkin_at, "distance_m": s.checkin_distance_m, "outside_geofence": far})


class StopOutcome(APIView):
    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        s = get_object_or_404(VisitStop, pk=pk, removed=False)
        if is_field_staff(request) and s.assigned_staff_id != request.user.pk:
            return Response(status=403)
        s = domain_call(
            v.record_outcome,
            s,
            request.data.get("outcome", ""),
            user=request.user,
            reasons=request.data.get("reasons", []),
            note=request.data.get("note", ""),
        )
        return Response({"outcome": s.outcome})


class SyncView(APIView):
    """OFF-10/11: the field app replays its offline queue here."""

    permission_classes = [IsBrokerMember]

    def post(self, request):
        muts = request.data.get("mutations", [])
        if not isinstance(muts, list) or len(muts) > 500:
            return Response({"detail": "mutations must be a list of at most 500"}, status=400)
        if any("idempotency_key" not in m for m in muts):
            return Response({"detail": "every mutation needs an idempotency_key"}, status=400)
        results = v.apply_mutations(
            org_id=request.user.active_org_id, user=request.user, device_id=str(request.data.get("device_id", "unknown")), mutations=muts
        )
        # Return the fresh server state of today's plans so the device can reconcile.
        today = [plan_json(p) for p in _plans(request).filter(date=timezone.localdate())]
        return Response({"results": results, "plans": today})


class PublicPlanView(PublicLinkMixin, APIView):
    def get(self, request, token):
        data = domain_call(v.public_plan_view, token)
        data.pop("org_id", None)
        return Response(data)

    def post(self, request, token):
        slot = request.data.get("slot")
        p = domain_call(v.customer_confirms, token, slot=datetime.fromisoformat(slot) if slot else None)
        return Response({"state": p.state})


class PublicVisitNoticeView(PublicLinkMixin, APIView):
    def post(self, request, token):
        s = domain_call(v.owner_acknowledges, token, bool(request.data.get("ok", True)))
        return Response({"owner_notice": s.owner_notice})
