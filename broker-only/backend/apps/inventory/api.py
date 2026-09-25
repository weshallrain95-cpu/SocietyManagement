from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.masterdata.layout import check_flat, issues_json
from apps.masterdata.models import MicroMarket, ResolvedAttribute, Society, Unit
from apps.masterdata.services import get_or_create_building, get_or_create_unit
from apps.orgs.permissions import IsBrokerManager, IsBrokerMember
from apps.owners.media import media_json
from apps.owners.services import flat_media, pending_media
from apps.status.models import UnitStatus
from common.api import domain_call, is_field_staff
from common.crypto import mask_phone

from . import browse, flatpage, services, upload
from .models import KeyCustody, Listing, UploadBatch, UploadRow

TXN = ["RENT", "SALE_NEW", "SALE_RESALE"]


def staff_listing_ids(request):
    from apps.visits.models import VisitStop

    return VisitStop.objects.filter(assigned_staff=request.user, removed=False).values_list("listing_id", flat=True)


def directions_url(point) -> str | None:
    """Google Maps directions from wherever the broker is to the flat's wing (the unit's own pin if set)."""
    return f"https://www.google.com/maps/dir/?api=1&destination={point.y},{point.x}" if point else None


def listing_json(l: Listing, request, *, detail=False, summary=False) -> dict:
    u = l.unit
    st = UnitStatus.objects.filter(unit=u, txn_type=l.txn_type).first()
    manager = request.user.active_membership.can_manage
    data = {
        "id": str(l.id),
        "txn_type": l.txn_type,
        "unit_id": str(u.id),
        "society": u.building.society.canonical_name,
        "society_id": str(u.building.society_id),
        "building": u.building.name,
        "unit_no": u.unit_no,
        "floor": u.floor,
        "bhk": float(u.bhk),
        "asking_rent": l.asking_rent,
        "asking_price": l.asking_price,
        "deposit": l.deposit,
        "available_from": l.available_from,
        "status": st.state if st else "UNKNOWN",
        "status_label": st.label if st else "Status unknown",
        "last_confirmed_at": l.last_confirmed_at,
        "origin": l.origin,
        "owner_appointed": l.origin == Listing.Origin.OWNER_INVITE,
        "owner_withdrew": l.withdrawn_by_owner,
        "visibility": l.visibility,
        "stale": (timezone.now() - l.last_confirmed_at).days >= (21 if l.txn_type == "RENT" else 45),
        "carpet_sqft": float(u.carpet_sqft) if u.carpet_sqft else None,
        "locality": u.building.society.locality.name if u.building.society.locality_id else "",
        "directions_url": directions_url(u.effective_location),
    }
    if summary:
        live = [] if l.withdrawn_by_owner else list(flat_media(u))
        photos = [m for m in live if m.kind == "photo"]
        key = services.current_keys(l)
        data.update(
            {
                "photo_count": len(photos),
                "has_video": any(m.kind == "video" for m in live),
                "thumb_url": media_json(photos[0], request)["thumb_url"] if photos else None,
                "keys_holder": key.holder_type if key else None,
                "owner_name": l.owner_name if manager else "",
            }
        )
    if detail:
        key = services.current_keys(l)
        data.update(
            {
                "maintenance": l.maintenance,
                "negotiable": l.negotiable,
                "brokerage_terms": l.brokerage_terms,
                "owner_name": l.owner_name,
                "owner_phone": (l.owner_phone if manager else mask_phone(l.owner_phone)),
                "private_notes": l.private_notes if manager else "",
                "keys": {
                    "holder_type": key.holder_type,
                    "holder_user_id": str(key.holder_user_id) if key.holder_user_id else None,
                    "instructions": key.instructions,
                    "needs_handover": key.needs_handover,
                }
                if key
                else None,
                "attributes": {
                    ra.attr_id: {"value": ra.value, "source": ra.resolved_source_type, "disputed": ra.disputed}
                    for ra in ResolvedAttribute.objects.filter(subject_id__in=[u.pk, u.building_id, u.building.society_id])
                },
                # Owner photos/videos: every broker holding the flat sees them, unless the owner removed the firm.
                "media": [] if l.withdrawn_by_owner else [media_json(x, request) for x in flat_media(u)],
                "my_pending_media": [media_json(x, request) for x in pending_media(u, org=l.org)],
                "page": {
                    **flatpage.sections(l),
                    "fitting_customers": flatpage.fitting_customers(l) if manager else {"count": 0, "customers": []},
                    "activity": flatpage.activity(l) if manager else [],
                    "other_brokers": flatpage.other_brokers(l) if manager else None,
                    "owner_on_platform": flatpage.owner_on_platform(l),
                },
            }
        )
    return data


class ListingCreateSerializer(serializers.Serializer):
    society_id = serializers.UUIDField()
    building = serializers.CharField(required=False, allow_blank=True, max_length=80)
    unit_no = serializers.CharField(max_length=30)
    floor = serializers.IntegerField(required=False, allow_null=True)
    confirm_layout = serializers.BooleanField(required=False, default=False, help_text="Save despite layout warnings")
    bhk = serializers.DecimalField(max_digits=3, decimal_places=1, min_value=Decimal("0.5"), max_value=Decimal("10"))
    property_type = serializers.ChoiceField(choices=Unit.PropertyType.choices, default="apartment")
    txn_type = serializers.ChoiceField(choices=TXN)
    asking_rent = serializers.IntegerField(required=False, min_value=1000, max_value=10_000_000)
    asking_price = serializers.IntegerField(required=False, min_value=100_000)
    deposit = serializers.IntegerField(required=False, min_value=0)
    maintenance = serializers.IntegerField(required=False, min_value=0)
    negotiable = serializers.BooleanField(required=False)
    available_from = serializers.DateField(required=False)
    brokerage_terms = serializers.CharField(required=False, allow_blank=True, max_length=200)
    owner_name = serializers.CharField(required=False, allow_blank=True, max_length=120)
    owner_phone = serializers.CharField(required=False, allow_blank=True)
    private_notes = serializers.CharField(required=False, allow_blank=True)
    visibility = serializers.ChoiceField(choices=Listing.Visibility.choices, required=False)
    attributes = serializers.DictField(required=False)
    keys = serializers.DictField(required=False)

    def validate(self, d):
        if d["txn_type"] == "RENT" and not d.get("asking_rent"):
            raise serializers.ValidationError({"asking_rent": "Rent is required for a rental listing"})
        if d["txn_type"] != "RENT" and not d.get("asking_price"):
            raise serializers.ValidationError({"asking_price": "Price is required for a sale listing"})
        return d


class ListingListCreate(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        qs = Listing.objects.filter(archived_at__isnull=True).select_related("unit__building__society__locality").order_by("-updated_at")
        if is_field_staff(request):
            qs = qs.filter(pk__in=staff_listing_ids(request))
        for f in ("txn_type",):
            if request.query_params.get(f):
                qs = qs.filter(**{f: request.query_params[f]})
        if request.query_params.get("society_id"):
            qs = qs.filter(unit__building__society_id=request.query_params["society_id"])
        if request.query_params.get("status"):
            qs = qs.filter(unit__statuses__state__in=request.query_params["status"].split(","), unit__statuses__txn_type__in=TXN).distinct()
        return Response([listing_json(l, request) for l in qs[:500]])

    def post(self, request):
        if not request.user.active_membership.can_manage:
            return Response({"detail": "Field staff cannot create listings; suggest a correction instead."}, status=403)
        s = ListingCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = dict(s.validated_data)
        org = request.user.active_membership.org
        society = get_object_or_404(Society, pk=d.pop("society_id"))
        if society.status == Society.Status.PROVISIONAL and society.proposed_by_org_id != org.pk:
            return Response({"detail": "That society is awaiting approval"}, status=400)
        society = society.resolved()
        # MD-13: the wing must exist and the flat number must fit the wing's floors and flats per floor.
        chk = check_flat(society, d.pop("building", "") or None, d["unit_no"], d.get("floor"))
        confirmed = d.pop("confirm_layout", False)
        if chk["blocking"] or (chk["issues"] and not confirmed):
            first = next((i for i in chk["issues"] if i.blocking), chk["issues"][0])
            return Response({"detail": first.message, "layout": issues_json(chk)}, status=422 if chk["blocking"] else 409)
        with transaction.atomic():
            building = get_or_create_building(society, chk["wing"])
            unit, _ = get_or_create_unit(
                building, d.pop("unit_no"), bhk=d["bhk"], property_type=d.pop("property_type"), floor=d.get("floor")
            )
            listing, created = domain_call(
                services.create_listing,
                org=org,
                user=request.user,
                unit=unit,
                txn_type=d.pop("txn_type"),
                data=d,
                attributes=d.pop("attributes", {}),
                owner_phone=d.pop("owner_phone", None) or None,
                keys=d.pop("keys", None),
            )
        return Response(listing_json(listing, request, detail=True), status=201 if created else 200)


class ListingBrowse(APIView):
    """GET /listings/browse?q=&txn_type=&status=&bhk=1,2&price_min=&price_max=&locality_id=&society_id=&building_id=
    &quick=reconfirm|new|keys_office|no_photos&sort=confirmed|newest|price_low|price_high&offset=&limit=

    The flat list for a broker with 1,000+ flats: one search box (society, flat number, owner name or phone),
    filters, quick views with counts, and paging."""

    permission_classes = [IsBrokerMember]

    def _base(self, request):
        qs = Listing.objects.all()
        if is_field_staff(request):
            qs = qs.filter(pk__in=staff_listing_ids(request))
        return qs

    def get(self, request):
        rows, total, counts = browse.browse(self._base(request), request.query_params, org=request.user.active_membership.org)
        return Response({"count": total, "counts": counts, "results": [listing_json(l, request, summary=True) for l in rows]})


class ListingsBySociety(ListingBrowse):
    """GET /listings/by-society — society → wing → how many of the broker's flats."""

    def get(self, request):
        return Response(browse.by_society(self._base(request)))


class ListingSearch(APIView):
    """GET /listings/search?q=HE A-1203 — jump straight to a flat the broker has in mind."""

    permission_classes = [IsBrokerMember]

    def get(self, request):
        from .search import search_flats

        qs = Listing.objects.all()
        if is_field_staff(request):
            qs = qs.filter(pk__in=staff_listing_ids(request))
        r = search_flats(qs, request.query_params.get("q", "")[:100], org=request.user.active_membership.org)
        return Response(
            {
                "results": [listing_json(l, request) for l in r["results"]],
                "unit_no": r["unit_no"],
                "wing": r["wing"],
            }
        )


class ListingMediaUpload(APIView):
    """POST a photo/video for a flat this firm holds; it goes live only when the owner approves (D15)."""

    permission_classes = [IsBrokerMember]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        from apps.owners.services import broker_add_media

        qs = Listing.objects.all()
        if is_field_staff(request):
            qs = qs.filter(pk__in=staff_listing_ids(request))  # staff can add photos for flats on their route
        l = get_object_or_404(qs, pk=pk)
        f = request.FILES.get("file")
        if f is None:
            return Response({"detail": "Choose a photo or video"}, status=400)
        item = domain_call(broker_add_media, l, f, user=request.user, caption=request.data.get("caption", ""))
        return Response(media_json(item, request), status=201)


class AskOwnerBack(APIView):
    """POST {note}: after the owner removed the firm, ask to be allowed again (the owner decides)."""

    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        from apps.owners.services import ask_owner_back

        l = get_object_or_404(Listing, pk=pk)
        domain_call(ask_owner_back, l.org, l.unit, note=str(request.data.get("note", "")), user=request.user)
        return Response({"detail": "Sent. The owner will decide."}, status=202)


class ListingDetail(APIView):
    permission_classes = [IsBrokerMember]

    def _get(self, request, pk):
        qs = Listing.objects.select_related("unit__building__society__locality")
        if is_field_staff(request):
            qs = qs.filter(pk__in=staff_listing_ids(request))
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        return Response(listing_json(self._get(request, pk), request, detail=True))

    def patch(self, request, pk):
        if not request.user.active_membership.can_manage:
            return Response(status=403)
        l = self._get(request, pk)
        allowed = {k: v for k, v in request.data.items() if k in services.LISTING_FIELDS or k in ("attributes", "owner_phone")}
        with transaction.atomic():
            domain_call(
                services.create_listing,
                org=l.org,
                user=request.user,
                unit=l.unit,
                txn_type=l.txn_type,
                data={k: v for k, v in allowed.items() if k in services.LISTING_FIELDS},
                attributes=allowed.get("attributes"),
                owner_phone=allowed.get("owner_phone"),
                report_available=False,
            )
        return Response(listing_json(self._get(request, pk), request, detail=True))

    def delete(self, request, pk):
        if not request.user.active_membership.can_manage:
            return Response(status=403)
        l = self._get(request, pk)
        l.archived_at = timezone.now()
        l.save(update_fields=["archived_at"])
        return Response(status=204)


class StatusReportSerializer(serializers.Serializer):
    state = serializers.ChoiceField(choices=["AVAILABLE", "ON_HOLD", "LET", "SOLD", "OFF_MARKET"])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=300)
    available_from = serializers.DateField(required=False)
    licence_end_date = serializers.DateField(required=False)
    on_behalf_of_owner = serializers.BooleanField(default=False)


class ListingStatusView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        s = StatusReportSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        l = get_object_or_404(Listing, pk=pk, archived_at__isnull=True)
        st = domain_call(
            services.report_status,
            l,
            d["state"],
            user=request.user,
            reason=d.get("reason", ""),
            available_from=d.get("available_from"),
            licence_end_date=d.get("licence_end_date"),
            on_behalf_of_owner=d["on_behalf_of_owner"],
        )
        return Response({"state": st.state, "label": st.label, "confirmed_by_owner": st.confirmed_by_owner})


class ListingReconfirmView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        l = get_object_or_404(Listing, pk=pk, archived_at__isnull=True)
        st = domain_call(services.report_status, l, "AVAILABLE", user=request.user, reason="reconfirmed")
        return Response({"state": st.state, "label": st.label})


class KeysView(APIView):
    permission_classes = [IsBrokerMember]

    def put(self, request, pk):
        l = get_object_or_404(Listing, pk=pk)
        holder = request.data.get("holder_type")
        if holder not in KeyCustody.Holder.values:
            return Response({"detail": f"holder_type must be one of {KeyCustody.Holder.values}"}, status=400)
        if (
            is_field_staff(request)
            and not (holder == "staff" and str(request.data.get("holder_user_id")) == str(request.user.pk))
            and holder not in ("office", "owner", "society_office", "lockbox")
        ):
            return Response(status=403)
        from apps.identity.models import User

        hu = User.objects.filter(pk=request.data.get("holder_user_id")).first() if request.data.get("holder_user_id") else None
        k = services.set_keys(l, holder_type=holder, holder_user=hu, instructions=request.data.get("instructions", ""))
        return Response({"holder_type": k.holder_type, "from": k.from_ts})


class CopyAttributesView(APIView):
    """docs/06 rule 5: 'Same as 1103?' copies the sibling unit's reported attributes in one tap."""

    permission_classes = [IsBrokerManager]
    FLOOR_SPECIFIC = {"floor_no", "view", "floor_pref_band"}

    def post(self, request, pk):
        from apps.masterdata import resolver

        l = get_object_or_404(Listing, pk=pk)
        sibling = get_object_or_404(Unit, pk=request.data.get("from_unit_id"), building=l.unit.building)
        n = 0
        with transaction.atomic():
            for ra in ResolvedAttribute.objects.filter(subject_type="unit", subject_id=sibling.pk).select_related("attr"):
                if ra.attr_id in self.FLOOR_SPECIFIC or ra.attr.scope == "listing" or ra.attr.authority == "computed":
                    continue
                resolver.record(l.unit, ra.attr_id, ra.value, source_type="broker", user=request.user, org=l.org, confidence=0.8)
                n += 1
        return Response({"copied": n})


# --- uploads -------------------------------------------------------------------


class UploadCreateView(APIView):
    permission_classes = [IsBrokerManager]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "Attach an .xlsx or .csv file"}, status=400)
        if f.size > 10 * 1024 * 1024 or not f.name.lower().endswith((".xlsx", ".csv")):
            return Response({"detail": "Only .xlsx or .csv up to 10 MB"}, status=400)
        mm = MicroMarket.objects.filter(pk=request.data.get("micro_market_id")).first() if request.data.get("micro_market_id") else None
        mapping = request.data.get("mapping")
        if isinstance(mapping, str) and mapping:
            import json

            mapping = json.loads(mapping)
        batch = domain_call(
            upload.create_batch,
            org=request.user.active_membership.org,
            user=request.user,
            filename=f.name,
            content=f.read(),
            micro_market=mm,
            default_txn_type=request.data.get("default_txn_type", "RENT"),
            mapping=mapping or None,
        )
        return Response(batch_json(batch), status=201)


def batch_json(b):
    return {
        "id": str(b.id),
        "filename": b.filename,
        "state": b.state,
        "counts": b.counts,
        "column_mapping": b.column_mapping,
        "created_at": b.created_at,
    }


class UploadDetailView(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request, pk):
        return Response(batch_json(get_object_or_404(UploadBatch, pk=pk)))


class UploadRowsView(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request, pk):
        qs = get_object_or_404(UploadBatch, pk=pk).rows.all()
        if request.query_params.get("resolution"):
            qs = qs.filter(resolution__in=request.query_params["resolution"].split(","))
        return Response(
            [
                {
                    "id": str(r.id),
                    "row_no": r.row_no,
                    "raw": r.raw,
                    "parsed": r.parsed,
                    "resolution": r.resolution,
                    "candidates": r.candidates,
                    "errors": r.errors,
                    "society_id": str(r.society_id) if r.society_id else None,
                }
                for r in qs[:2000]
            ]
        )


class UploadRowResolveView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk, row_id):
        row = get_object_or_404(UploadRow, pk=row_id, batch_id=pk)
        r = domain_call(
            upload.resolve_row,
            row,
            user=request.user,
            society_id=request.data.get("society_id"),
            propose=request.data.get("propose"),
            skip=bool(request.data.get("skip")),
        )
        return Response({"id": str(r.id), "resolution": r.resolution})


class UploadCommitView(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        return Response(upload.commit_batch(get_object_or_404(UploadBatch, pk=pk), user=request.user))


class UploadTemplateView(APIView):
    """The starter template: essentials + popular optional columns (docs/06 rule 6)."""

    permission_classes = [IsBrokerMember]

    def get(self, request):
        import io

        from django.http import HttpResponse
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Flats"
        ws.append(
            [
                "Society",
                "Wing",
                "Flat No",
                "BHK",
                "Rent",
                "Price",
                "Deposit",
                "Available From",
                "Owner",
                "Owner Mobile",
                "Furnishing",
                "Pets",
                "Parking",
                "Non Veg",
                "Bachelors",
                "Notes",
            ]
        )
        ws.append(
            [
                "Hiranandani Estate",
                "Rodas A",
                "1203",
                "2",
                "25000",
                "",
                "75000",
                "01/11/2026",
                "Owner name",
                "98XXXXXXXX",
                "semi-furnished",
                "yes",
                "1",
                "allowed",
                "not allowed",
                "example row – delete me",
            ]
        )
        buf = io.BytesIO()
        wb.save(buf)
        resp = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = 'attachment; filename="only-broker-inventory-template.xlsx"'
        return resp
