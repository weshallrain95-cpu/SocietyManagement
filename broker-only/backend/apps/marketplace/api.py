from django.contrib.gis.geos import Point
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit
from apps.orgs.permissions import IsBrokerManager, IsBrokerMember
from apps.orgs.serializers import PublicBrokerSerializer
from common.api import PublicLinkThrottle, domain_call

from . import services as mkt
from . import supply
from .models import Enquiry, EnquiryDelivery, Proposal


class MapView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [PublicLinkThrottle]

    def get(self, request):
        try:
            bbox = tuple(float(x) for x in request.query_params["bbox"].split(","))
            assert len(bbox) == 4
            zoom = float(request.query_params.get("zoom", 13))
        except (KeyError, ValueError, AssertionError):
            return Response({"detail": "bbox=min_lng,min_lat,max_lng,max_lat and zoom are required"}, status=400)
        return Response(
            supply.map_view(bbox=bbox, zoom=zoom, txn_type=request.query_params.get("txn", "RENT"), bhk=request.query_params.get("bhk"))
        )


class EnquirySerializer(serializers.Serializer):
    txn_type = serializers.ChoiceField(choices=["RENT", "SALE_NEW", "SALE_RESALE"])
    property_types = serializers.ListField(child=serializers.CharField(), required=False)
    bhk_min = serializers.DecimalField(max_digits=3, decimal_places=1)
    bhk_max = serializers.DecimalField(max_digits=3, decimal_places=1)
    budget_min = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    budget_max = serializers.IntegerField(min_value=1000)
    center = serializers.DictField()
    radius_m = serializers.IntegerField(default=3000, min_value=500, max_value=15000)
    area_label = serializers.CharField(required=False, allow_blank=True, max_length=120)
    must_haves = serializers.DictField(required=False)
    house_rule_needs = serializers.DictField(required=False)
    max_station_distance_m = serializers.IntegerField(required=False, allow_null=True)
    move_in_by = serializers.DateField(required=False, allow_null=True)
    urgency = serializers.ChoiceField(choices=["normal", "urgent"], default="normal")
    occupants = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=30)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, d):
        d["center"] = Point(float(d["center"]["lng"]), float(d["center"]["lat"]), srid=4326)
        if d["bhk_min"] > d["bhk_max"]:
            raise serializers.ValidationError("bhk_min must be ≤ bhk_max")
        return d


def enquiry_json(e: Enquiry, *, for_customer=False):
    d = {
        "id": str(e.id),
        "summary": e.summary_text,
        "state": e.state,
        "txn_type": e.txn_type,
        "created_at": e.created_at,
        "expires_at": e.expires_at,
        "urgency": e.urgency,
        "radius_m": e.radius_m,
        "area_label": e.area_label,
    }
    if for_customer:
        d["recipients"] = e.n_recipients
        d["proposals"] = e.proposals.count()
    return d


def proposal_json(p: Proposal):
    return {
        "id": str(p.id),
        "state": p.state,
        "broker": PublicBrokerSerializer(p.org).data,
        "brokerage_terms": p.brokerage_terms,
        "message": p.message,
        "match_count": p.match_count,
        "earliest_slot": p.earliest_slot,
        "response_s": p.response_s,
        "promoted": p.promoted,
        "created_at": p.created_at,
    }


class EnquiryListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            [enquiry_json(e, for_customer=True) for e in Enquiry.objects.filter(customer_user=request.user).order_by("-created_at")[:50]]
        )

    def post(self, request):
        s = EnquirySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        e = domain_call(mkt.create_enquiry, request.user, s.validated_data)
        return Response(enquiry_json(e, for_customer=True), status=201)


class EnquiryDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        e = get_object_or_404(Enquiry, pk=pk, customer_user=request.user)
        ranked = sorted(e.proposals.select_related("org"), key=lambda p: (-p.promoted, -float(p.org.rating_bayes), p.response_s))
        return Response({**enquiry_json(e, for_customer=True), "proposals": [proposal_json(p) for p in ranked]})


class EnquiryClose(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        e = get_object_or_404(Enquiry, pk=pk, customer_user=request.user)
        state = request.data.get("state", "cancelled")
        if state not in ("cancelled", "fulfilled"):
            return Response(status=400)
        return Response(enquiry_json(mkt.close_enquiry(request.user, e, state), for_customer=True))


class ProposalAccept(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        p = get_object_or_404(Proposal, pk=pk, enquiry__customer_user=request.user)
        return Response(proposal_json(domain_call(mkt.accept_proposal, request.user, p)))


class BrokerLeads(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        org_id = request.user.active_org_id
        mine = {p.enquiry_id: p for p in Proposal.objects.filter(org_id=org_id)}
        out = []
        for d in EnquiryDelivery.objects.filter(org_id=org_id).select_related("enquiry").order_by("-created_at")[:200]:
            p = mine.get(d.enquiry_id)
            out.append({**enquiry_json(d.enquiry), "match_count": d.match_count, "my_proposal": p.state if p else None})
        EnquiryDelivery.objects.filter(org_id=org_id, seen_at__isnull=True).update(seen_at=timezone.now())
        return Response(out)


class ProposalCreate(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        e = get_object_or_404(Enquiry, pk=pk)
        slot = request.data.get("earliest_slot")
        from django.utils.dateparse import parse_datetime

        p = domain_call(
            mkt.send_proposal,
            request.user.active_membership.org,
            request.user,
            e,
            brokerage_terms=str(request.data.get("brokerage_terms", ""))[:200] or "As discussed",
            message=str(request.data.get("message", "")),
            earliest_slot=parse_datetime(slot) if slot else None,
        )
        return Response(proposal_json(p), status=201)


class EnquiryReport(APIView):
    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        e = get_object_or_404(Enquiry, pk=pk, deliveries__org_id=request.user.active_org_id)
        mkt.report_fake(request.user.active_membership.org, e, str(request.data.get("reason", "")))
        return Response({"reported": True})


class PresenceView(APIView):
    """Online for enquiries (MKT-11): on from sign-up until the broker goes offline. The app's
    live connection still heartbeats, which only decides instant alert vs push."""

    def get_permissions(self):
        return [IsBrokerMember()] if self.request.method == "GET" else [IsBrokerManager()]

    def get(self, request):
        return Response({"online": request.user.active_membership.org.accepting_enquiries})

    def post(self, request):
        org = request.user.active_membership.org
        online = bool(request.data.get("online", True))
        if org.accepting_enquiries != online:
            with transaction.atomic():
                org.accepting_enquiries = online
                org.save(update_fields=["accepting_enquiries", "updated_at"])
                audit(request.user, "broker_org.online" if online else "broker_org.offline", org, {})
        return Response({"online": org.accepting_enquiries})
