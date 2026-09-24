"""Owner API (/v1/owner/...), the broker's invitation inbox, and signed media delivery."""

import os
import re

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.masterdata.layout import layout_dict
from apps.masterdata.models import OwnershipClaim, Society
from apps.orgs.models import BrokerOrg
from apps.orgs.permissions import IsBrokerManager, IsBrokerMember
from common.api import domain_call

from . import services as svc
from .media import check_signature, media_json
from .models import OwnerInvite, UnitMedia


def _claim(request, pk) -> OwnershipClaim:
    return get_object_or_404(svc.my_claims(request.user), pk=pk)


def flat_json(c: OwnershipClaim, request, *, detail=False) -> dict:
    u = c.unit
    b = u.building
    data = {
        "id": str(c.pk),
        "unit_id": str(u.pk),
        "society": b.society.canonical_name,
        "society_id": str(b.society_id),
        "locality": b.society.locality.name,
        "building": b.name,
        "unit_no": u.unit_no,
        "floor": u.floor,
        "bhk": float(u.bhk),
        "claim_status": c.status,
        "terms": c.terms,
        "photo_count": svc.flat_media(u, kinds=("photo",)).count(),
        "video_count": svc.flat_media(u, kinds=("video",)).count(),
    }
    view = svc.flat_view(c)
    data["statuses"] = view["statuses"]
    data["brokers"] = view["brokers"]
    if detail:
        data["invites"] = view["invites"]
        data["media"] = [media_json(x, request) for x in svc.flat_media(u)]
        data["proof_on_file"] = UnitMedia.objects.filter(claim=c, kind="document", deleted_at__isnull=True).exists()
        data["layout"] = layout_dict(b)
    return data


class RegisterSerializer(serializers.Serializer):
    society_id = serializers.UUIDField()
    wing = serializers.CharField(required=False, allow_blank=True)
    unit_no = serializers.CharField(max_length=30)
    floor = serializers.IntegerField(required=False, allow_null=True)
    bhk = serializers.DecimalField(max_digits=3, decimal_places=1)
    declared = serializers.BooleanField()
    proof = serializers.FileField()


class OwnerFlats(APIView):
    """GET my flats · POST register a flat (multipart, with a proof document)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        return Response([flat_json(c, request) for c in svc.my_claims(request.user)])

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        society = get_object_or_404(Society, pk=d["society_id"], status__in=["active", "merged"])
        c = domain_call(
            svc.register_flat,
            request.user,
            society=society,
            wing=d.get("wing") or None,
            unit_no=d["unit_no"],
            bhk=d["bhk"],
            floor=d.get("floor"),
            proof=d["proof"],
            declared=d["declared"],
        )
        return Response(flat_json(c, request, detail=True), status=201)


class OwnerFlatDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        return Response(flat_json(_claim(request, pk), request, detail=True))


class OwnerTerms(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        c = _claim(request, pk)
        domain_call(
            svc.set_terms, c, terms=request.data.get("terms") or {}, house_rules=request.data.get("house_rules") or {}, user=request.user
        )
        return Response(flat_json(c, request, detail=True))


class OwnerMedia(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        c = _claim(request, pk)
        f = request.FILES.get("file")
        if f is None:
            return Response({"detail": "Choose a photo or video"}, status=400)
        item = domain_call(svc.add_media, c, f, user=request.user, caption=request.data.get("caption", ""))
        return Response(media_json(item, request), status=201)


class OwnerMediaDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, media_id):
        item = get_object_or_404(UnitMedia, pk=media_id, deleted_at__isnull=True, kind__in=["photo", "video"])
        _claim_for_unit = svc.my_claims(request.user).filter(unit=item.unit).exists()
        if not _claim_for_unit:
            return Response(status=404)
        svc.delete_media(item, user=request.user)
        return Response(status=204)


class OwnerBrokersNearby(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        return Response(svc.brokers_nearby(_claim(request, pk)))


class OwnerInviteView(APIView):
    """POST {org_id, allow: true} — allow must be the owner's own tick."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        c = _claim(request, pk)
        org = get_object_or_404(BrokerOrg, pk=request.data.get("org_id"), verification_status="verified")
        inv = domain_call(svc.invite, c, org, allow=request.data.get("allow") is True, user=request.user)
        return Response({"id": str(inv.pk), "state": inv.state, "allowed_at": inv.allowed_at.isoformat()}, status=201)


class OwnerAllowBroker(APIView):
    """POST {allowed: bool, reason?} — untick to remove a broker from the flat; tick to allow them again."""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, org_id):
        c = _claim(request, pk)
        org = get_object_or_404(BrokerOrg, pk=org_id)
        if not isinstance(request.data.get("allowed"), bool):
            return Response({"detail": "allowed must be true or false"}, status=400)
        domain_call(svc.set_allowed, c, org, request.data["allowed"], user=request.user, reason=str(request.data.get("reason", "")))
        return Response(flat_json(c, request, detail=True))


class OwnerReviewBroker(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, org_id):
        c = _claim(request, pk)
        org = get_object_or_404(BrokerOrg, pk=org_id)
        r = domain_call(
            svc.review_broker,
            c,
            org,
            stars=request.data.get("stars", 0),
            tags=request.data.get("tags") or [],
            text=request.data.get("text", ""),
            user=request.user,
        )
        return Response({"id": str(r.pk), "stars": r.stars}, status=201)


# --- broker side -------------------------------------------------------------------------------------------


def invite_json(i: OwnerInvite) -> dict:
    u = i.unit
    return {
        "id": str(i.pk),
        "state": i.state,
        "society": u.building.society.canonical_name,
        "locality": u.building.society.locality.name,
        "building": u.building.name,
        "unit_no": u.unit_no,
        "bhk": float(u.bhk),
        "txn_type": i.txn_type,
        "terms": i.terms,
        "owner_name": i.owner.display_name or "Owner",
        "allowed_at": i.allowed_at.isoformat(),
        "listing_id": str(i.listing_id) if i.listing_id else None,
    }


class BrokerInvites(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        qs = OwnerInvite.objects.select_related("unit__building__society__locality", "owner").order_by("-created_at")
        if request.query_params.get("state", "pending") != "all":
            qs = qs.filter(state=OwnerInvite.State.PENDING)
        return Response([invite_json(i) for i in qs[:100]])


class BrokerInviteAction(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk, action):
        inv = get_object_or_404(OwnerInvite, pk=pk)  # RLS: only this firm's invitations are visible
        if action == "accept":
            listing = domain_call(svc.accept_invite, inv, user=request.user)
            return Response({"listing_id": str(listing.pk), **invite_json(inv)})
        if action == "decline":
            domain_call(svc.decline_invite, inv, user=request.user)
            return Response(invite_json(inv))
        return Response({"detail": "Unknown action"}, status=404)


# --- signed media delivery -------------------------------------------------------------------------------

_RANGE = re.compile(r"bytes=(\d*)-(\d*)")


def media_file(request, pk, variant):
    """GET /m/<id>/<full|thumb>?e=…&s=… — whoever holds a fresh signed link may view the file."""
    if variant not in ("full", "thumb") or not check_signature(pk, variant, request.GET.get("e", ""), request.GET.get("s", "")):
        raise Http404
    item = UnitMedia.objects.filter(pk=pk, deleted_at__isnull=True).first()
    if item is None:
        raise Http404
    f = item.thumb if variant == "thumb" and item.thumb else item.file
    ctype = "image/jpeg" if f is item.thumb else item.content_type
    size = f.size
    rng = _RANGE.fullmatch(request.headers.get("Range", ""))
    if rng and (rng.group(1) or rng.group(2)):  # videos seek with byte ranges (Safari needs this)
        start = int(rng.group(1)) if rng.group(1) else max(0, size - int(rng.group(2)))
        end = min(int(rng.group(2)), size - 1) if rng.group(1) and rng.group(2) else size - 1
        if start >= size:
            resp = HttpResponse(status=416)
            resp["Content-Range"] = f"bytes */{size}"
            return resp
        with f.open("rb") as fh:
            fh.seek(start)
            body = fh.read(min(end - start + 1, 8 * 1024 * 1024))
        resp = HttpResponse(body, status=206, content_type=ctype)
        resp["Content-Range"] = f"bytes {start}-{start + len(body) - 1}/{size}"
    else:
        resp = FileResponse(f.open("rb"), content_type=ctype)
        resp["Content-Length"] = str(size)
    resp["Accept-Ranges"] = "bytes"
    resp["Cache-Control"] = "private, max-age=3600"
    resp["X-Content-Type-Options"] = "nosniff"
    resp["Content-Disposition"] = f'inline; filename="{os.path.basename(f.name)}"'
    return resp
