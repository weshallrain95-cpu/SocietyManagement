from django.contrib.gis.geos import Point
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orgs.permissions import IsBrokerMember, IsPlatformAdmin
from common.api import domain_call
from common.models import ReviewQueueItem
from common.notify import queue_for_admin
from common.rls import platform_context

from . import dedupe, resolver, services
from .layout import check_flat, issues_json, layout_dict
from .location import facts_dict
from .models import AttributeDef, Building, Locality, MicroMarket, ResolvedAttribute, Society, Unit


class SocietySearchView(APIView):
    """Typo-tolerant society search used by every 'pick a society' screen."""

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if len(q) < 2:
            return Response({"results": []})
        point = None
        if "lat" in request.query_params and "lng" in request.query_params:
            point = Point(float(request.query_params["lng"]), float(request.query_params["lat"]), srid=4326)
        mm = (
            MicroMarket.objects.filter(pk=request.query_params["micro_market"]).first()
            if request.query_params.get("micro_market")
            else None
        )
        org = getattr(getattr(request.user, "active_membership", None), "org", None)
        cands = dedupe.find_candidates(q, point=point, micro_market=mm, include_provisional_for_org=org, limit=8)
        return Response({"results": [c.as_dict() for c in cands]})


def resolved_for(subject_type, subject_id, public_only=False) -> dict:
    qs = ResolvedAttribute.objects.filter(subject_type=subject_type, subject_id=subject_id).select_related("attr")
    out = {}
    for ra in qs:
        if public_only and ra.attr.public == "N":
            continue
        out[ra.attr_id] = {
            "label": ra.attr.label,
            "category": ra.attr.category,
            "value": ra.value,
            "source": ra.resolved_source_type,
            "disputed": ra.disputed,
        }
    return out


class SocietyDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        s = get_object_or_404(Society.objects.select_related("locality"), pk=pk)
        s = s.resolved()
        buildings = [
            {
                "id": str(b.id),
                "name": b.name,
                "floors_total": b.floors_total,
                "layout": layout_dict(b),
                "location_facts": facts_dict(b),
                "attributes": resolved_for("building", b.id),
            }
            for b in s.buildings.filter(merged_into__isnull=True).prefetch_related("location_facts")
        ]
        return Response(
            {
                "id": str(s.id),
                "name": s.canonical_name,
                "status": s.status,
                "locality": s.locality.name,
                "pincode": s.pincode,
                "location": {"lat": s.location.y, "lng": s.location.x},
                "rera_project_nos": s.rera_project_nos,
                "wings_complete": s.wings_complete,
                "attributes": resolved_for("society", s.id),
                "buildings": buildings,
            }
        )


class CheckFlatView(APIView):
    """Live check while the broker types: does this wing and flat number exist?"""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        s = get_object_or_404(Society, pk=pk).resolved()
        q = request.query_params
        floor = q.get("floor")
        result = check_flat(s, q.get("wing") or None, q.get("unit_no", ""), int(floor) if floor and floor.lstrip("-").isdigit() else None)
        return Response(issues_json(result))


class LayoutReportView(APIView):
    """'This flat really exists': the broker tells ops the building record is wrong."""

    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        b = get_object_or_404(Building, pk=pk)
        org = request.user.active_membership.org
        unit_no = str(request.data.get("unit_no", ""))[:30]
        note = str(request.data.get("note", ""))[:200]
        with platform_context():
            queue_for_admin(
                "layout_report",
                b.society,
                f"{org.name}: flat {unit_no} in {b.name}, {b.society.canonical_name} was refused by the layout. {note}".strip(),
                {"building_id": str(b.pk), "unit_no": unit_no, "org_id": str(org.pk)},
            )
        return Response({"detail": "Thanks — our team will check the building record, usually within a day."}, status=202)


class BuildingUnitsView(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request, pk):
        b = get_object_or_404(Building, pk=pk)
        units = b.units.filter(merged_into__isnull=True).order_by("floor", "unit_no_normalised")
        return Response([{"id": str(u.id), "unit_no": u.unit_no, "floor": u.floor, "bhk": float(u.bhk)} for u in units])


class UnitCardView(APIView):
    """Everything known about a unit, resolved, with sources. Flat number only for brokers."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        from apps.status.models import UnitStatus

        u = get_object_or_404(Unit.objects.select_related("building__society__locality"), pk=pk)
        broker = bool(getattr(request.user, "active_membership", None))
        attrs = {}
        for scope, sid in (("society", u.building.society_id), ("building", u.building_id), ("unit", u.pk)):
            attrs.update(resolved_for(scope, sid, public_only=not broker))
        statuses = [
            {"txn_type": s.txn_type, "state": s.state, "label": s.label, "since": s.since} for s in UnitStatus.objects.filter(unit=u)
        ]
        return Response(
            {
                "id": str(u.id),
                "society": u.building.society.canonical_name,
                "building": u.building.name,
                "unit_no": u.unit_no if broker else None,
                "floor": u.floor,
                "bhk": float(u.bhk),
                "property_type": u.property_type,
                "locality": u.building.society.locality.name,
                "location_facts": facts_dict(u.building),
                "attributes": attrs,
                "status": statuses,
            }
        )


class DictionaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = AttributeDef.objects.filter(active=True).order_by("display_order")
        if request.query_params.get("tier"):
            qs = qs.filter(entry_tier__in=request.query_params["tier"].split(","))
        if request.query_params.get("txn"):
            qs = qs.filter(applies_to__contains=[request.query_params["txn"]])
        if request.query_params.get("matchable"):
            qs = qs.filter(matching__in=["hard", "soft"])
        return Response(
            [
                {
                    "key": a.key,
                    "label": a.label,
                    "category": a.category,
                    "scope": a.scope,
                    "type": a.value_type,
                    "values": a.allowed_values,
                    "unit": a.unit_label,
                    "matching": a.matching,
                    "tier": a.entry_tier,
                    "asked_of": a.asked_of,
                }
                for a in qs
            ]
        )


class SuggestionSerializer(serializers.Serializer):
    attr = serializers.CharField()
    value = serializers.JSONField()


class AttributeSuggestionView(APIView):
    """MD-10: anyone who has seen the flat can suggest a correction; trust weighting decides."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        s = SuggestionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        u = get_object_or_404(Unit, pk=pk)
        m = getattr(request.user, "active_membership", None)
        source = "broker" if m else "customer"
        obs = domain_call(
            resolver.record,
            u,
            s.validated_data["attr"],
            s.validated_data["value"],
            source_type=source,
            user=request.user,
            org=m.org if m else None,
        )
        if obs is None:
            return Response({"detail": "Unknown attribute"}, status=400)
        return Response({"recorded": True}, status=201)


class ProposeSocietySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    locality_id = serializers.UUIDField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    address = serializers.CharField(required=False, allow_blank=True, max_length=300)
    pincode = serializers.RegexField(r"^\d{6}$", required=False, allow_blank=True)


class ProposeSocietyView(APIView):
    permission_classes = [IsBrokerMember]

    def post(self, request):
        s = ProposeSocietySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        locality = get_object_or_404(Locality, pk=d["locality_id"])
        point = Point(d["lng"], d["lat"], srid=4326)
        cands = dedupe.find_candidates(d["name"], point=point, locality=locality)
        decision = dedupe.decide(cands)
        if decision.action == "auto" and not request.data.get("force"):
            return Response({"detail": "This society already exists", "existing": decision.best.as_dict()}, status=409)
        with transaction.atomic():
            soc = services.propose_society(
                name=d["name"],
                locality=locality,
                location=point,
                org=request.user.active_membership.org,
                address=d.get("address", ""),
                pincode=d.get("pincode", ""),
                user=request.user,
            )
            queue_for_admin(
                "provisional_society", soc, f"New society proposed: {soc.canonical_name}", {"candidates": [c.as_dict() for c in cands[:3]]}
            )
        return Response({"id": str(soc.id), "status": soc.status}, status=201)


class LocalityListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Locality.objects.select_related("micro_market").order_by("micro_market__name", "name")
        return Response(
            [
                {
                    "id": str(l.id),
                    "name": l.name,
                    "micro_market": l.micro_market.name,
                    "centroid": {"lat": l.centroid.y, "lng": l.centroid.x},
                }
                for l in qs
            ]
        )


# --- admin ------------------------------------------------------------------


class AdminQueueView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        qs = ReviewQueueItem.objects.filter(state=request.query_params.get("state", "open")).order_by("-created_at")
        if request.query_params.get("kind"):
            qs = qs.filter(kind=request.query_params["kind"])
        return Response(
            [
                {
                    "id": str(i.id),
                    "kind": i.kind,
                    "ref_type": i.ref_type,
                    "ref_id": i.ref_id,
                    "summary": i.summary,
                    "data": i.data,
                    "created_at": i.created_at,
                }
                for i in qs[:200]
            ]
        )


class AdminQueueResolveView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, pk):
        i = get_object_or_404(ReviewQueueItem, pk=pk, state="open")
        i.state, i.resolved_by, i.resolved_at = "resolved", request.user, timezone.now()
        i.resolution = (request.data.get("resolution") or "")[:300]
        i.save()
        return Response({"id": str(i.id), "state": i.state})


class AdminMergeView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, pk):
        src = get_object_or_404(Society, pk=pk)
        dst = get_object_or_404(Society, pk=request.data.get("into"))
        with platform_context():
            result = domain_call(services.merge_societies, src, dst, user=request.user)
        return Response(result)


class AdminApproveSocietyView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, pk):
        s = get_object_or_404(Society, pk=pk, status=Society.Status.PROVISIONAL)
        services.approve_provisional(s, user=request.user)
        return Response({"id": str(s.id), "status": s.status})
