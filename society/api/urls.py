from django.urls import path
from rest_framework.routers import DefaultRouter

from society.api.views.audit import AuditEventViewSet
from society.api.views.audit_verification import AuditVerificationAPIView

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="audit-events")

urlpatterns = [
    # 🔐 IMPORTANT: custom endpoint FIRST
    path("audit-events/verify/", AuditVerificationAPIView.as_view()),
]

urlpatterns += router.urls
