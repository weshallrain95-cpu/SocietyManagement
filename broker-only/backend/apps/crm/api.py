from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.serializers import PhoneField
from apps.inventory.models import Listing
from apps.masterdata.models import Locality
from apps.matching.services import match_requirement
from apps.orgs.permissions import CanDo, IsBrokerManager, IsBrokerMember
from common.api import PublicLinkMixin, domain_call, is_field_staff
from common.crypto import mask_phone

from . import services as crm
from .models import Customer, Requirement, Shortlist


def customer_json(c: Customer, request, detail=False):
    manager = request.user.active_membership.can_manage
    d = {
        "id": str(c.id),
        "name": c.name,
        "phone": c.phone if manager else mask_phone(c.phone),
        "source": c.source,
        "stage": c.stage,
        "consent_state": c.consent_state,
        "can_message": c.can_message,
        "on_platform": bool(c.platform_user_id),
        "next_follow_up": c.next_follow_up,
        "tags": c.tags,
        "created_at": c.created_at,
    }
    if detail:
        d["notes"] = c.notes
        d["requirements"] = [requirement_json(r) for r in c.requirements.filter(active=True).order_by("-created_at")]
    return d


def requirement_json(r: Requirement):
    return {
        "id": str(r.id),
        "txn_type": r.txn_type,
        "bhk_min": float(r.bhk_min),
        "bhk_max": float(r.bhk_max),
        "budget_min": r.budget_min,
        "budget_max": r.budget_max,
        "must_haves": r.must_haves,
        "nice_to_haves": r.nice_to_haves,
        "house_rule_needs": r.house_rule_needs,
        "max_station_distance_m": r.max_station_distance_m,
        "occupants": r.occupants,
        "move_in_by": r.move_in_by,
        "version": r.version,
        "summary": crm.describe(r),
        "localities": [str(i) for i in r.localities.values_list("id", flat=True)],
    }


def _customers(request):
    qs = Customer.objects.all()
    if is_field_staff(request):
        # Customers on their visits, plus walk-ins they captured themselves.
        qs = qs.filter(Q(visit_plans__stops__assigned_staff=request.user) | Q(created_by=request.user)).distinct()
    return qs


class CaptureSerializer(serializers.Serializer):
    phone = PhoneField()
    name = serializers.CharField(required=False, allow_blank=True, max_length=120)
    source = serializers.ChoiceField(choices=Customer.Source.choices, default="walk_in")
    notes = serializers.CharField(required=False, allow_blank=True)


class CustomerImport(APIView):
    """CRM-11: bring the existing customer list in (Excel / CSV / phone contacts .vcf, or pasted lines as `text`)."""

    permission_classes = [CanDo("uploads")]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        f = request.FILES.get("file")
        if f is not None:
            if f.size > 5 * 1024 * 1024:
                return Response({"detail": "Keep the file under 5 MB"}, status=400)
            name, content = f.name, f.read()
        elif request.data.get("text"):
            name, content = "pasted.txt", str(request.data["text"]).encode()
        else:
            return Response({"detail": "Attach a file or paste the list"}, status=400)
        org = request.user.active_membership.org
        return Response(domain_call(crm.import_customers, org=org, user=request.user, filename=name, content=content))


class CustomerListCreate(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        qs = _customers(request).order_by("-updated_at")
        if request.query_params.get("stage"):
            qs = qs.filter(stage=request.query_params["stage"])
        if request.query_params.get("q"):
            q = request.query_params["q"]
            try:
                from common.crypto import normalise_phone, phone_hash

                qs = qs.filter(phone_hash=phone_hash(normalise_phone(q)))
            except ValueError:
                qs = qs.filter(name__icontains=q)
        return Response([customer_json(c, request) for c in qs[:500]])

    def post(self, request):
        """OFF-01 quick capture: phone + name + source, ≤ 60 s. Field staff can capture walk-ins too."""
        s = CaptureSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        c, created = crm.capture_customer(org=request.user.active_membership.org, user=request.user, **s.validated_data)
        if not created and is_field_staff(request) and not _customers(request).filter(pk=c.pk).exists():
            # Already the agency's customer: field staff learn only that, not the record.
            return Response({"detail": "This customer is already with your agency. Tell your manager they walked in."}, status=409)
        return Response(customer_json(c, request, detail=True), status=201 if created else 200)


class CustomerDetail(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request, pk):
        return Response(customer_json(get_object_or_404(_customers(request), pk=pk), request, detail=True))

    def patch(self, request, pk):
        if not request.user.active_membership.can_manage:
            return Response(status=403)
        c = get_object_or_404(Customer, pk=pk)
        for f in ("name", "stage", "lost_reason", "tags", "notes", "next_follow_up"):
            if f in request.data:
                setattr(c, f, request.data[f])
        if c.stage not in Customer.Stage.values:
            return Response({"detail": "Unknown stage"}, status=400)
        c.save()
        return Response(customer_json(c, request, detail=True))


class TimelineView(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request, pk):
        c = get_object_or_404(_customers(request), pk=pk)
        return Response(
            [
                {
                    "id": str(i.id),
                    "kind": i.kind,
                    "summary": i.summary,
                    "at": i.occurred_at,
                    "duration_s": i.duration_s,
                    "by": i.by_user.display_name if i.by_user else None,
                }
                for i in c.interactions.select_related("by_user")[:300]
            ]
        )


class InteractionCreate(APIView):
    """OFF-07: log calls, office meetings and WhatsApp chats against the customer."""

    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        c = get_object_or_404(_customers(request), pk=pk)
        kind = request.data.get("kind")
        if kind not in {"call_in", "call_out", "office_meeting", "whatsapp", "sms", "note"}:
            return Response({"detail": "Unknown interaction kind"}, status=400)
        i = crm.log(c, kind, request.data.get("summary", ""), user=request.user, duration_s=request.data.get("duration_s"))
        return Response({"id": str(i.id)}, status=201)


class ConsentView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        c = get_object_or_404(Customer, pk=pk)
        out = domain_call(
            crm.request_consent, c, method=request.data.get("method", "link"), user=request.user, note=request.data.get("note", "")
        )
        out.pop("token", None)  # the link goes to the customer's phone, never back to the broker
        return Response(out)


class ConsentVerifyView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        c = get_object_or_404(Customer, pk=pk)
        domain_call(crm.confirm_consent_otp, c, str(request.data.get("code", "")), user=request.user)
        return Response({"consent_state": Customer.objects.get(pk=pk).consent_state})


class RequirementSerializer(serializers.Serializer):
    txn_type = serializers.ChoiceField(choices=["RENT", "SALE_NEW", "SALE_RESALE"])
    bhk_min = serializers.DecimalField(max_digits=3, decimal_places=1)
    bhk_max = serializers.DecimalField(max_digits=3, decimal_places=1)
    budget_min = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    budget_max = serializers.IntegerField(min_value=1000)
    property_types = serializers.ListField(child=serializers.CharField(), required=False)
    locality_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
    center = serializers.DictField(required=False)
    radius_m = serializers.IntegerField(required=False, min_value=300, max_value=25000)
    max_station_distance_m = serializers.IntegerField(required=False, allow_null=True)
    must_haves = serializers.DictField(required=False)
    nice_to_haves = serializers.DictField(required=False)
    house_rule_needs = serializers.DictField(required=False)
    move_in_by = serializers.DateField(required=False, allow_null=True)
    occupants = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=30)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, d):
        if d["bhk_min"] > d["bhk_max"]:
            raise serializers.ValidationError("bhk_min must be ≤ bhk_max")
        if "center" in d:
            from django.contrib.gis.geos import Point

            from apps.marketplace.services import circle

            d["search_area"] = circle(Point(float(d["center"]["lng"]), float(d["center"]["lat"]), srid=4326), d.pop("radius_m", 3000))
            d.pop("center")
        d.pop("radius_m", None)
        return d


class RequirementCreate(APIView):
    permission_classes = [IsBrokerMember]

    def post(self, request, pk):
        # Field staff may note what a walk-in they captured is looking for; managers for any customer.
        base = Customer.objects.filter(created_by=request.user) if is_field_staff(request) else Customer.objects.all()
        c = get_object_or_404(base, pk=pk)
        s = RequirementSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        localities = Locality.objects.filter(pk__in=d.pop("locality_ids", []))
        r = crm.add_requirement(c, d, localities=localities)
        return Response(requirement_json(r), status=201)


class RequirementDetail(APIView):
    permission_classes = [IsBrokerManager]

    def patch(self, request, pk):
        r = get_object_or_404(Requirement, pk=pk)
        s = RequirementSerializer(data={**requirement_json(r), **request.data})
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        locs = d.pop("locality_ids", None)
        r = crm.update_requirement(r, d)
        if locs is not None:
            r.localities.set(Locality.objects.filter(pk__in=locs))
        return Response(requirement_json(r))


class MatchView(APIView):
    """MATCH-01..05: ranked matches from the broker's own listings, with reasons."""

    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        r = get_object_or_404(Requirement, pk=pk)
        run = match_requirement(r, include_unconfirmed=request.data.get("include_unconfirmed", True))
        from apps.inventory.api import listing_json

        results = []
        for mr in run.results.select_related("listing__unit__building__society"):
            if mr.excluded and not request.data.get("include_excluded"):
                continue
            results.append(
                {"listing": listing_json(mr.listing, request), "score": mr.score, "excluded": mr.excluded, "explanation": mr.explanation}
            )
        return Response({"run_id": str(run.id), "considered": run.n_considered, "matched": run.n_matched, "results": results})


class ShortlistCreate(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        c = get_object_or_404(Customer, pk=pk)
        listings = list(Listing.objects.filter(pk__in=request.data.get("listing_ids", [])))
        sl = domain_call(
            crm.create_shortlist,
            c,
            listings,
            title=request.data.get("title", ""),
            requirement=Requirement.objects.filter(pk=request.data.get("requirement_id")).first()
            if request.data.get("requirement_id")
            else None,
        )
        return Response({"id": str(sl.id), "items": sl.items.count()}, status=201)


class ShortlistShare(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        sl = get_object_or_404(Shortlist, pk=pk)
        domain_call(crm.share_shortlist, sl, user=request.user)
        return Response({"shared_at": Shortlist.objects.get(pk=pk).shared_at})


# --- public pages for offline customers ---------------------------------------


class PublicShortlistView(PublicLinkMixin, APIView):
    def get(self, request, token):
        return Response(domain_call(crm.public_shortlist, token))


class PublicShortlistRespond(PublicLinkMixin, APIView):
    def post(self, request, token, item_id):
        it = domain_call(crm.respond_to_shortlist_item, token, item_id, request.data.get("response", ""))
        return Response({"response": it.customer_response})


class PublicConsentView(PublicLinkMixin, APIView):
    def post(self, request, token):
        c = domain_call(crm.confirm_consent_link, token, agree=bool(request.data.get("agree")))
        return Response({"consent_state": c.consent_state, "at": timezone.now()})
