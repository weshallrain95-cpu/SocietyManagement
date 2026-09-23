from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.api import PublicLinkMixin, domain_call

from . import services
from .models import Interaction, Review


class BrokerReviews(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        qs = Review.objects.filter(org_id=pk, direction="C2B", moderation_state="published").order_by("-created_at")[:100]
        return Response(
            [
                {
                    "stars": r.stars,
                    "tags": r.tags,
                    "text": r.text,
                    "reply": r.reply_text,
                    "label": r.reviewer_label or "Verified customer",
                    "verified_visit": True,
                    "at": r.created_at,
                }
                for r in qs
            ]
        )


class InteractionReview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        inter = get_object_or_404(Interaction, pk=pk)
        r = domain_call(
            services.submit,
            inter,
            reviewer=request.user,
            direction=request.data.get("direction", "C2B"),
            stars=request.data.get("stars", 0),
            tags=request.data.get("tags", []),
            text=request.data.get("text", ""),
        )
        return Response({"id": str(r.id)}, status=201)


class PublicReview(PublicLinkMixin, APIView):
    def post(self, request, token):
        r = domain_call(
            services.review_via_link,
            token,
            stars=request.data.get("stars", 0),
            tags=request.data.get("tags", []),
            text=request.data.get("text", ""),
        )
        return Response({"id": str(r.id), "thank_you": True}, status=201)
