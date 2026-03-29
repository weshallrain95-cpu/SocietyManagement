from django.urls import path
from rest_framework.routers import DefaultRouter

from society.api.views.audit import AuditEventViewSet
from society.api.views.audit_verification import AuditVerificationAPIView
from society.api.views.signup import signup_create_society
from society.api.views.mobile_check import mobile_exists
from society.api.views.otp_verify import verify_otp
from society.api.views.user_societies import get_user_societies
from society.api.views.structure import generate_structure
from society.api.views.excel import download_structure_excel
from society.api.views.ownership_upload import upload_ownership_excel
from society.api.views.onboarding_status import get_onboarding_status
from .views.flats import get_flats
from .views.ownership import get_ownership, update_ownership
from society.api.views.onboarding_complete import complete_onboarding

router = DefaultRouter()
router.register("audit-events", AuditEventViewSet, basename="audit-events")

urlpatterns = [
    # Audit
    path("audit-events/verify/", AuditVerificationAPIView.as_view()),

    # Auth / Signup
    path("signup/", signup_create_society),
    path("mobile-exists/", mobile_exists),
    path("verify-otp/", verify_otp),
    path("user-societies/", get_user_societies),

    # Structure Engine
    path("structure/generate/", generate_structure),

    # ✅ SINGLE DOWNLOAD ENDPOINT
    path("structure/download-excel/", download_structure_excel),

    # ✅ SINGLE UPLOAD ENDPOINT
    path("structure/upload-ownership/", upload_ownership_excel),

    path("onboarding/status/", get_onboarding_status),
    path("flats/", get_flats),
    path("ownership/", get_ownership),
    path("ownership/update/", update_ownership),
    path("onboarding/complete/", complete_onboarding),

]

urlpatterns += router.urls
