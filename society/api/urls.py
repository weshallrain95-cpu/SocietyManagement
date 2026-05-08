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
from society.api.views.committee import create_committee
from society.api.views.members import list_members
from society.api.views.committee import create_full_committee
from society.api.views.onboarding_complete import mark_governance_complete
from society.api.views.society_details import get_society_details
from society.api.views.bylaws_generate import generate_bylaws
from society.api.views.bylaws_schema import get_bylaw_schema
from society.api.views.bylaws_generate import download_bylaws
from society.api.views.bylaws_upload import upload_signed_bylaws
from society.api.views.bylaws_status import bylaws_status
from society.api.views.share_certificates import (
    preview_share_certificates,
    generate_share_certificates,
)
from society.api.views.operational_rules import (
    get_operational_rules,
    save_operational_rules,
)
from .views.billing_rules import get_billing_rules, save_billing_rules
from society.api.views.share_certificates import issue_share_certificates
from society.api.views.document_generation import generate_document
from society.api.views.society_update import update_society
from society.api.views.artifact_status import get_artifact_status
from society.api.views.artifact_download import download_artifact
from society.api.views.artifact_upload import upload_artifact
from society.api.views.test_forma_access import test_forma_access
from society.api.views.update_registration import update_registration
from society.api.views.ledger_views import transfer_ledger_view
from society.api.views.coa_list import get_coa_list
from society.api.views.billing import generate_bill
from society.api.views.update_registration_docs import update_registration_docs
from society.api.views.financial_onboarding import financial_onboarding_state


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
    path("committee/create/", create_committee),
    path("members/", list_members),
    path("committee/full-create/", create_full_committee),
    path("onboarding/governance-complete/", mark_governance_complete),
    path("details/", get_society_details),
    path("bylaws/generate/", generate_bylaws),
    path("bylaws/schema/", get_bylaw_schema),
    path("bylaws/download/", download_bylaws),
    path("bylaws/upload/", upload_signed_bylaws),
    path("bylaws/status/", bylaws_status),
    path(
        "share-certificates/preview/",
        preview_share_certificates
    ),
    path("share-certificates/generate/", generate_share_certificates),
    path(
        "share-certificates/issue/",
        issue_share_certificates
    ),
    path("billing-rules/", get_billing_rules),
    path("billing-rules/save/", save_billing_rules),
    path("operational-rules/", get_operational_rules),
    path("operational-rules/save/", save_operational_rules),
    path("documents/generate/", generate_document),
    path("update/", update_society),
    path("artifacts/status/", get_artifact_status),
    path("artifacts/download/", download_artifact),
    path("artifacts/upload/", upload_artifact),
    path("test-forma-access/", test_forma_access),
    path("update-registration/", update_registration),
    path("api/ledger/transfers/", transfer_ledger_view),
    path("coa/list/", get_coa_list),
    path("billing/generate/", generate_bill),
    path("update-registration-docs/", update_registration_docs),
    path("financial-onboarding/state/",financial_onboarding_state,),
]

urlpatterns += router.urls
