from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from society.audit_verifier import verify_audit_chain


class AuditVerificationAPIView(APIView):
    """
    Verifies audit event hash chain integrity.
    Read-only, admin-only.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        is_valid, error = verify_audit_chain()

        if is_valid:
            return Response(
                {
                    "status": "ok",
                    "message": "Audit chain is valid",
                }
            )

        return Response(
            {
                "status": "corrupted",
                "message": "Audit chain integrity violation detected",
                "details": error,
            },
            status=500,
        )
