from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from common import crypto

from . import otp
from .models import User
from .serializers import MeSerializer, OtpRequestSerializer, OtpVerifySerializer, SwitchRoleSerializer
from .tokens import issue_tokens


class OtpThrottle(AnonRateThrottle):
    scope = "otp"


class OtpRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        s = OtpRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            code = otp.request_otp(s.validated_data["phone"])
        except otp.OtpError as e:
            return Response({"detail": str(e)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        body = {"detail": "OTP sent", "expires_in_s": int(otp.TTL.total_seconds())}
        if code:
            body["dev_code"] = code  # console provider in DEBUG only
        return Response(body)


class OtpVerifyView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        s = OtpVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data["phone"]
        try:
            with transaction.atomic():
                ph = otp.verify_otp(phone, s.validated_data["code"])
        except otp.OtpError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(phone_hash=ph).first()
        created = user is None
        if created:
            user = User.objects.create_user(phone, display_name=s.validated_data.get("display_name", ""))
        if not user.is_active:
            return Response({"detail": "Account suspended"}, status=status.HTTP_403_FORBIDDEN)
        _link_offline_customer_records(user)
        # Default to the user's first active broker membership if they have one.
        m = user.memberships.filter(active=True).order_by("created_at").first()
        role = m.role if m else ("owner" if user.ownership_claims.exists() else "customer")
        tokens = issue_tokens(user, org_id=m.org_id if m else None, role=role)
        return Response({**tokens, "new_user": created}, status=status.HTTP_200_OK)


def _link_offline_customer_records(user):
    """OFF-09: a customer a broker served offline claims their records on first login."""
    from apps.crm.services import link_platform_user

    link_platform_user(user)


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)

    def patch(self, request):
        s = MeSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        for k, v in s.validated_data.items():
            setattr(request.user, k, v)
        request.user.save()
        return Response(MeSerializer(request.user).data)


class SwitchRoleView(APIView):
    def post(self, request):
        s = SwitchRoleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        role, org_id = s.validated_data["role"], s.validated_data.get("org_id")
        if role == "broker":
            m = request.user.memberships.filter(active=True, **({"org_id": org_id} if org_id else {})).first()
            if not m:
                return Response({"detail": "You are not a member of that broker organisation."}, status=403)
            return Response(issue_tokens(request.user, org_id=m.org_id, role=m.role))
        return Response(issue_tokens(request.user, role=role))


__all__ = ["OtpRequestView", "OtpVerifyView", "MeView", "SwitchRoleView", "crypto"]
