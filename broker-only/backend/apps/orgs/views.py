from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import audit
from apps.identity.models import User
from apps.identity.tokens import issue_tokens

from .models import BrokerOrg, Membership, ServiceArea
from .permissions import IsBrokerAdmin, IsBrokerManager, IsBrokerMember, IsPlatformAdmin
from .serializers import (
    BrokerOrgSerializer,
    MembershipSerializer,
    PublicBrokerSerializer,
    ServiceAreaSerializer,
    StaffInviteSerializer,
)

ONE_AGENCY = "This number already belongs to an agency. One phone number can be part of one agency only."
ONE_AGENCY_OTHER = "This number already belongs to another agency. One phone number can be part of one agency only."


class BrokerOrgCreateView(APIView):
    """Any signed-in user can start a broker org and becomes its principal."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = BrokerOrgSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        if request.user.memberships.filter(active=True).exists():
            return Response({"detail": ONE_AGENCY}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            org = s.save()
            Membership.objects.create(user=request.user, org=org, role=Membership.Role.PRINCIPAL)
            audit(request.user, "broker_org.created", org, {"name": org.name})
        return Response(
            {"org": BrokerOrgSerializer(org).data, "tokens": issue_tokens(request.user, org_id=org.id, role="broker_principal")},
            status=status.HTTP_201_CREATED,
        )


class MyOrgView(APIView):
    permission_classes = [IsBrokerMember]

    def get(self, request):
        return Response(BrokerOrgSerializer(request.user.active_membership.org).data)

    def patch(self, request):
        if not request.user.active_membership.is_admin:
            return Response({"detail": "Only the agency Admin can change the agency's details."}, status=status.HTTP_403_FORBIDDEN)
        s = BrokerOrgSerializer(request.user.active_membership.org, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(s.data)


class StaffView(APIView):
    permission_classes = [IsBrokerManager]

    def get(self, request):
        qs = Membership.objects.filter(org_id=request.user.active_org_id).select_related("user").order_by("created_at")
        return Response(MembershipSerializer(qs, many=True).data)

    def post(self, request):
        s = StaffInviteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        me = request.user.active_membership
        role = s.validated_data["role"]
        if role == Membership.Role.MANAGER and not me.is_admin:
            return Response({"detail": "Only the agency Admin can add managers."}, status=403)
        if role == Membership.Role.STAFF and not me.can("add_staff"):
            return Response({"detail": "Ask the agency Admin to add field staff, or to allow you to."}, status=403)
        phone = s.validated_data["phone"]
        with transaction.atomic():
            try:
                user = User.objects.get_by_phone(phone)
            except User.DoesNotExist:
                user = User.objects.create_user(phone, display_name=s.validated_data.get("display_name", ""))
            if user.memberships.filter(active=True).exclude(org_id=request.user.active_org_id).exists():
                return Response({"detail": ONE_AGENCY_OTHER}, status=400)
            m, created = Membership.objects.get_or_create(
                user=user, org_id=request.user.active_org_id, active=True, defaults={"role": s.validated_data["role"]}
            )
            audit(request.user, "broker_org.staff_added", m, {"role": m.role})
        return Response(MembershipSerializer(m).data, status=201 if created else 200)


class MemberPermissionsView(APIView):
    """PUT {permissions: [...]}: the Admin switches uploads / blasts / add_staff on or off for a manager."""

    permission_classes = [IsBrokerAdmin]

    def put(self, request, membership_id):
        m = get_object_or_404(Membership, id=membership_id, org_id=request.user.active_org_id, active=True)
        if m.role != Membership.Role.MANAGER:
            return Response({"detail": "Only managers have these switches."}, status=400)
        wanted = request.data.get("permissions")
        if not isinstance(wanted, list) or any(p not in Membership.DELEGABLE for p in wanted):
            return Response({"detail": f"permissions must be a list drawn from {list(Membership.DELEGABLE)}"}, status=400)
        before = list(m.permissions)
        m.permissions = [p for p in Membership.DELEGABLE if p in wanted]
        m.save(update_fields=["permissions", "updated_at"])
        audit(request.user, "broker_org.permissions_changed", m, {"before": before, "after": m.permissions})
        return Response(MembershipSerializer(m).data)


class StaffRemoveView(APIView):
    permission_classes = [IsBrokerManager]

    def delete(self, request, membership_id):
        m = get_object_or_404(Membership, id=membership_id, org_id=request.user.active_org_id, active=True)
        me = request.user.active_membership
        if m.role == Membership.Role.PRINCIPAL:
            return Response({"detail": "The Admin cannot be removed."}, status=400)
        if (m.role == Membership.Role.MANAGER and not me.is_admin) or (m.role == Membership.Role.STAFF and not me.can("add_staff")):
            return Response({"detail": "Only the agency Admin can remove this person."}, status=403)
        with transaction.atomic():
            m.active = False
            m.ended_at = timezone.now()
            m.save(update_fields=["active", "ended_at"])
            from apps.inventory.services import flag_keys_for_handover

            flagged = flag_keys_for_handover(m.org_id, m.user_id)
            audit(request.user, "broker_org.staff_removed", m, {"keys_flagged": flagged})
        return Response({"keys_flagged_for_handover": flagged})


class ServiceAreaListCreate(generics.ListCreateAPIView):
    permission_classes = [IsBrokerAdmin]
    serializer_class = ServiceAreaSerializer
    pagination_class = None

    def get_queryset(self):
        return ServiceArea.objects.filter(org_id=self.request.user.active_org_id)

    def perform_create(self, serializer):
        serializer.save(org_id=self.request.user.active_org_id)


class ServiceAreaDelete(generics.DestroyAPIView):
    permission_classes = [IsBrokerAdmin]

    def get_queryset(self):
        return ServiceArea.objects.filter(org_id=self.request.user.active_org_id)


class PublicBrokerView(generics.RetrieveAPIView):
    serializer_class = PublicBrokerSerializer
    queryset = BrokerOrg.objects.filter(verification_status=BrokerOrg.Verification.VERIFIED)


class VerificationQueueView(generics.ListAPIView):
    permission_classes = [IsPlatformAdmin]
    serializer_class = BrokerOrgSerializer

    def get_queryset(self):
        return BrokerOrg.objects.filter(verification_status=BrokerOrg.Verification.PENDING).order_by("-created_at")


class VerificationDecisionView(APIView):
    permission_classes = [IsPlatformAdmin]

    def post(self, request, org_id):
        org = get_object_or_404(BrokerOrg, id=org_id)
        decision = request.data.get("decision")
        if decision not in ("verified", "rejected", "suspended"):
            return Response({"detail": "decision must be verified, rejected or suspended"}, status=400)
        org.verification_status = decision
        org.verification_note = (request.data.get("note") or "")[:300]
        if decision == "verified" and request.data.get("rera_verified") and org.rera_agent_no:
            org.rera_verified_at = timezone.now()
        org.save()
        audit(request.user, f"broker_org.{decision}", org, {"note": org.verification_note})
        return Response(BrokerOrgSerializer(org).data)
