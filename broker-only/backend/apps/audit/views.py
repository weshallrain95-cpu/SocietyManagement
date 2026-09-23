from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orgs.permissions import IsPlatformAdmin

from .services import verify_chain


class VerifyAuditView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        from apps.status.services import verify_ledger

        return Response({"audit": verify_chain(), "status_ledger": verify_ledger()})
