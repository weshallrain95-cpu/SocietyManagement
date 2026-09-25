"""Co-broking API (D17): the fellow-broker list, blasts to fellow brokers, and the trade inbox."""

from django.shortcuts import get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.masterdata.models import Locality
from apps.orgs.permissions import CanDo, IsBrokerManager
from common.api import domain_call

from . import services as svc
from .models import FellowBroker, TradeBlast, TradeDelivery


def _org(request):
    return request.user.active_membership.org


def _ids(v):
    if isinstance(v, str):
        return [x for x in v.split(",") if x]
    return list(v or [])


def _blast_args(src) -> dict:
    get = src.getlist if hasattr(src, "getlist") else None
    return {
        "kind": src.get("kind", "flats"),
        "listing_ids": _ids(get("listing_ids") if get and len(get("listing_ids")) > 1 else src.get("listing_ids")),
        "requirement_id": src.get("requirement_id") or None,
        "scope": src.get("scope", "radius"),
        "radius_km": src.get("radius_km") or svc.DEFAULT_RADIUS_KM,
        "contact_ids": _ids(get("contact_ids") if get and len(get("contact_ids")) > 1 else src.get("contact_ids")),
    }


class ContactListCreate(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request):
        qs = FellowBroker.objects.filter(active=True).select_related("locality", "platform_org").order_by("name")
        q = (request.query_params.get("q") or "").strip().lower()
        rows = [svc.contact_json(c) for c in qs]
        if q:
            rows = [r for r in rows if q in f"{r['name']} {r['firm']} {r['phone']} {r['locality'] or ''} {r['address']}".lower()]
        return Response(rows)

    def post(self, request):
        d = request.data
        loc = get_object_or_404(Locality, pk=d["locality_id"]) if d.get("locality_id") else None
        c, created = domain_call(
            svc.save_contact,
            _org(request),
            name=d.get("name", ""),
            phone=d.get("phone", ""),
            firm=d.get("firm", ""),
            address=d.get("address", ""),
            area=d.get("area", ""),
            locality=loc,
            lat=d.get("lat"),
            lng=d.get("lng"),
            notes=d.get("notes", ""),
        )
        return Response(svc.contact_json(c) | {"created": created}, status=201 if created else 200)


class ContactDetail(APIView):
    permission_classes = [IsBrokerManager]

    def delete(self, request, pk):
        c = get_object_or_404(FellowBroker, pk=pk)
        c.active = False
        c.save(update_fields=["active"])
        return Response(status=204)


class ContactImport(APIView):
    """Excel / CSV / phone contacts (.vcf) as a file, or pasted lines as `text`."""

    permission_classes = [IsBrokerManager]
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
        return Response(domain_call(svc.import_contacts, _org(request), filename=name, content=content))


class BlastPreview(APIView):
    """GET ?kind=flats&listing_ids=a,b | kind=requirement&requirement_id= &scope=radius|all|selected&radius_km=&contact_ids="""

    permission_classes = [CanDo("blasts")]

    def get(self, request):
        return Response(domain_call(svc.preview, _org(request), user=request.user, **_blast_args(request.query_params)))


class BlastListCreate(APIView):
    def get_permissions(self):
        return [IsBrokerManager()] if self.request.method == "GET" else [CanDo("blasts")()]

    def get(self, request):
        return Response([svc.blast_json(b) for b in TradeBlast.objects.order_by("-created_at")[:50]])

    def post(self, request):
        b, whatsapp = domain_call(
            svc.send, _org(request), user=request.user, text_=request.data.get("text", ""), **_blast_args(request.data)
        )
        return Response(svc.blast_json(b) | {"whatsapp": whatsapp}, status=201)


class BlastDetail(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request, pk):
        return Response(svc.blast_json(get_object_or_404(TradeBlast, pk=pk), with_replies=True))


class Inbox(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request):
        return Response([svc.delivery_json(d) for d in svc.inbox(_org(request))])

    def post(self, request):
        return Response({"marked_read": svc.mark_read(_org(request))})


class InboxReply(APIView):
    permission_classes = [IsBrokerManager]

    def post(self, request, pk):
        d = get_object_or_404(TradeDelivery, pk=pk)
        d = domain_call(
            svc.reply,
            d,
            org=_org(request),
            user=request.user,
            answer=request.data.get("answer", ""),
            message=request.data.get("message", ""),
        )
        return Response(svc.delivery_json(d))
