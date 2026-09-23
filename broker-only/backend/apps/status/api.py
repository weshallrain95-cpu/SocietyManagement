from rest_framework.response import Response
from rest_framework.views import APIView

from common.api import PublicLinkMixin, domain_call
from common.links import resolve_link
from common.models import ShareLink

from . import services
from .models import StatusConfirmation


class PublicConfirmationView(PublicLinkMixin, APIView):
    """STAT-05: the owner answers from a WhatsApp link, no app or login needed."""

    def get(self, request, token):
        link = domain_call(resolve_link, token, ShareLink.Purpose.STATUS_CONFIRMATION, consume=False)
        conf = StatusConfirmation.objects.select_related("unit__building__society").get(pk=link.target_id)
        u = conf.unit
        return Response(
            {
                "question": f"Is your flat {u.unit_no}, {u.building.name}, {u.building.society.canonical_name} available for "
                f"{'rent' if conf.txn_type == 'RENT' else 'sale'}?",
                "options": ["yes", "no", "available_from"],
                "answered": bool(conf.response),
            }
        )

    def post(self, request, token):
        link = domain_call(resolve_link, token, ShareLink.Purpose.STATUS_CONFIRMATION, consume=True)
        conf = StatusConfirmation.objects.get(pk=link.target_id)
        response = request.data.get("response")
        if response not in ("yes", "no", "available_from"):
            return Response({"detail": "response must be yes, no or available_from"}, status=400)
        from datetime import date

        when = date.fromisoformat(request.data["available_from"]) if response == "available_from" else None
        st = domain_call(services.owner_responds, conf, response, available_from=when)
        return Response({"thank_you": True, "status": st.label})
