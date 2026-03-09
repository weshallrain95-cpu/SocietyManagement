"""
Statutory Onboarding Engine
---------------------------
Chairman-first, checklist-driven statutory onboarding system.

Stage 0 focus:
- Society NOT yet formed
- User is legally unsure
- System guides via checklist + auto-generated artifacts
- Soft enforcement with auditability

This engine is PROCESS-AWARE, not UI-AWARE.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from django.db import transaction
import re
from statutory.preregistration.status import (
    is_preregistration_complete,
    preregistration_blockers,
)

# ------------------------------------------------------------------
# Artifact Context Contracts (Stage 0 – Maharashtra)
# ------------------------------------------------------------------
# These define the ONLY allowed placeholders for auto-population.
# They are legally sensitive and MUST remain explicit.
# ------------------------------------------------------------------

ARTIFACT_CONTEXT_CONTRACTS = {

    # --------------------------------------------------
    # FORM A — Application for Society Registration (MH)
    # --------------------------------------------------
    "FORM_A_MH": {
        "required": [
            "society_name",
            "society_address",
            "society_type",
            "area_of_operation",
            "first_meeting_date",
            "promoter_count",
            "chief_promoter_name",
            "chief_promoter_address",
            "chief_promoter_phone",
            "authorized_share_capital",
            "share_value",
            "bank_name",
            "bank_branch",
            "declaration_place",
            "declaration_date",
            "chief_promoter_signature",
        ],
        "optional": [],
        "rules": {
            "promoter_count": ">=10",
            "chief_promoter_phone": "indian_mobile",
            "authorized_share_capital": ">0",
            "share_value": ">0",
        },
        "description": (
            "Form A — Application for registration of a Cooperative "
            "Housing Society under Maharashtra Cooperative Societies Act"
        ),
    },

    # --------------------------------------------------
    # Provisional Managing Committee Resolution (MH)
    # --------------------------------------------------
    "PROVISIONAL_COMMITTEE_RESOLUTION_MH": {
        "required": [
            "society_name",
            "meeting_date",
            "meeting_place",
            "resolution_number",
            "chairman_name",
            "secretary_name",
            "committee_members",   # List[{name, role}]
            "resolution_text",
            "signatories",         # List[{name, role}]
        ],
        "optional": [],
        "rules": {},
        "description": (
            "Resolution appointing Provisional Managing Committee "
            "prior to society registration (Maharashtra)"
        ),
    },

    # --------------------------------------------------
    # Draft Bye-laws (MH)
    # --------------------------------------------------
    "BYLAW_DRAFT_MH": {
        "required": [
            "society_name",
            "registered_address",
            "district",
            "promoter_name",
            "total_flats",
            "adoption_date",
        ],
        "optional": [
            "registration_number",
            "taluka",
            "village",
        ],
        "rules": {
            "total_flats": ">0",
        },
        "description": (
            "Draft Bye-laws of a Cooperative Housing Society "
            "as per Maharashtra Cooperative Societies Rules"
        ),
    },
}


# Core system imports (already existing in your codebase)
from society.core.governance import GovernanceDecision
from society.core.events import EventBus

# Domain models (assumed existing / already seeded)
from statutory.models import (
    LegalStage,
    LegalObligation,
    LegalChecklistItem,
    LegalArtifactTemplate,
    SocietyLegalProgress,
    SocietyObligationStatus,
)

from society.models import Society


# ------------------------------------------------------------------
# Domain Exceptions (engine-level, not UI-level)
# ------------------------------------------------------------------

class OnboardingError(Exception):
    """Base onboarding exception"""


class GovernanceBlockedError(OnboardingError):
    """Raised when governance blocks an action"""


class ValidationError(OnboardingError):
    """Raised when checklist / artifact validation fails"""


class ConcurrencyError(OnboardingError):
    """Raised on duplicate or concurrent onboarding attempts"""


# ------------------------------------------------------------------
# DTOs (engine outputs – safe for UI / API)
# ------------------------------------------------------------------

@dataclass
class OnboardingStartResult:
    execution_id: str
    society_id: int
    stage: str
    status: str


@dataclass
class ChecklistItemDTO:
    id: int
    description: str
    mandatory: bool
    completed: bool


@dataclass
class ObligationDTO:
    id: int
    title: str
    mandatory: bool
    status: str
    checklist: List[ChecklistItemDTO]


# ------------------------------------------------------------------
# Core Engine
# ------------------------------------------------------------------
PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.]+)\s*}}")

class StatutoryOnboardingEngine:
    """
    Core onboarding engine.

    Responsibilities:
    - Start onboarding (Stage 0)
    - Attach legal stages & obligations
    - Expose checklist + artifacts
    - Validate or override obligations
    - Progress stages safely
    """

    def __init__(self, system=None):
        """
        system: SocietyOS system instance (optional but recommended)
        """
        self.system = system
        self.context = getattr(system, "context", None)
        self.governance = getattr(system, "governance", None)
        self.event_bus: Optional[EventBus] = getattr(system, "event_bus", None)

    # --------------------------------------------------------------
    # Governance helper
    # --------------------------------------------------------------

    def _governance_check(self, action: str, payload: Dict[str, Any]) -> None:
        if not self.governance:
            return

        decision: GovernanceDecision = self.governance.evaluate(
            self.context, action, payload
        )

        if not decision.allowed and self.governance.mode == "enforce":
            raise GovernanceBlockedError(decision.reason)
    
    # --------------------------------------------------------------
    # Template rendering helper (STRICT)
    # --------------------------------------------------------------

    def _render_template(
        self,
        template_body: str,
        context_data: Dict[str, Any],
        *,
        artifact_code: str,
    ) -> str:
        """
        Internal helper to render legal artifacts safely.

        Responsibilities:
        - Enforce artifact context contract
        - Reject missing mandatory fields
        - Perform deterministic placeholder substitution
        """

        # --------------------------------------------------
        # 1. HARD VALIDATION (THIS WAS MISSING)
        # --------------------------------------------------
        self._validate_artifact_context(
            artifact_code=artifact_code,
            context_data=context_data,
        )

        # --------------------------------------------------
        # 2. Deterministic placeholder substitution
        # --------------------------------------------------
        rendered = template_body

        for key, value in context_data.items():
            rendered = rendered.replace(
                "{{ " + key + " }}",
                str(value),
            )
        return rendered


        # --------------------------------------------------
        # 3. Render template
        # --------------------------------------------------
        rendered = template_body

        for key, value in context_data.items():
            rendered = rendered.replace(
                "{{ " + key + " }}",
                str(value),
            )

        return rendered

    # --------------------------------------------------------------
    # Entry point – Stage 0
    # --------------------------------------------------------------

    @transaction.atomic
    def start_onboarding(
        self,
        initiator_phone: str,
        society_data: Optional[Dict[str, Any]] = None,
        state_code: str = "MH",
        case: Optional["Case"] = None,
    ) -> OnboardingStartResult:
        """
        Start Stage 0 onboarding.

        Chairman-first:
        - Phone number is primary identifier
        - Society may not yet be registered
        """

        self._governance_check(
            "onboarding.start",
            {"phone": initiator_phone, "state": state_code},
        )

        # TODO: normalize & validate phone number

        # TODO: check one-time onboarding rule (deployment/society)

        # Create or reuse society draft
        society = self._create_or_get_society_draft(case, society_data)

        # Ensure SoftOnboardingTracker exists
        from society.models import SoftOnboardingTracker

        SoftOnboardingTracker.objects.get_or_create(
            society=society
        )

        # Seed statutory stages & obligations
        self._seed_legal_stages(society, state_code)

        # Create execution id (human-readable, audit-friendly)
        execution_id = f"onboard-{society.id}"

        return OnboardingStartResult(
            execution_id=execution_id,
            society_id=society.id,
            stage="Stage 0",
            status="IN_PROGRESS",
        )

    # --------------------------------------------------------------
    # Society draft handling
    # --------------------------------------------------------------

    def _create_or_get_society_draft(
        self,
        case,
        society_data: Optional[Dict[str, Any]]
    ) -> Society:
        """
        Create minimal Society record if not present.
        """
        if case and case.society:
            return case.society

        if not society_data:
            society_data = {"name": "Draft Society"}

        society = Society.objects.create(**society_data)

        if case:
            case.society = society
            case.save(update_fields=["society"])

        return society

    # --------------------------------------------------------------
    # Legal stage seeding
    # --------------------------------------------------------------

    def _seed_legal_stages(self, society: Society, state_code: str) -> None:
        """
        Attach LegalStage graph to society.
        """
        from statutory.models import State

        state_obj = State.objects.filter(code__iexact=state_code).first()

        if not state_obj:
            raise OnboardingError(f"Invalid state code: {state_code}")

        stages = LegalStage.objects.filter(
            state=state_obj
        ).order_by("sequence_order")

        if not stages.exists():
            raise OnboardingError(f"No legal stages found for state {state_code}")

        for stage in stages:
            SocietyLegalProgress.objects.get_or_create(
                society=society,
                legal_stage=stage,
                defaults={"status": "PENDING"},
            )

    # --------------------------------------------------------------
    # Read API – checklist-first view
    # --------------------------------------------------------------

    def get_stage_checklist(self, society: Society) -> List[ObligationDTO]:
        """
        Return current obligations as checklist-friendly DTOs.
        """

        obligations = LegalObligation.objects.filter(
            legal_stage__societylegalprogress__society=society
        )

        result: List[ObligationDTO] = []

        for obligation in obligations:
            checklist_items = LegalChecklistItem.objects.filter(
                legal_obligation=obligation
            )

            checklist_dtos = [
                ChecklistItemDTO(
                    id=item.id,
                    description=item.description,
                    mandatory=item.mandatory,
                    completed=False,  # TODO: wire real completion state
                )
                for item in checklist_items
            ]

            result.append(
                ObligationDTO(
                    id=obligation.id,
                    title=obligation.title,
                    mandatory=obligation.mandatory,
                    status="PENDING",  # TODO: derive from SocietyObligationStatus
                    checklist=checklist_dtos,
                )
            )

        return result

    # --------------------------------------------------------------
    # Artifact generation (critical for Stage 0 UX)
    # --------------------------------------------------------------

    def generate_artifact(
        self,
        obligation_id: int,
        context_data: Dict[str, Any],
    ) -> str:
        """
        Generate auto-filled legal artifact (Stage 0).

        Returns:
            Rendered document (text / HTML).
        """

        obligation = LegalObligation.objects.get(id=obligation_id)
        template = LegalArtifactTemplate.objects.filter(
            legal_obligation=obligation
        ).first()

        if not template:
            raise ValidationError("No artifact template found")

        artifact_code = template.artifact_type

        self._validate_artifact_context(
            artifact_code=artifact_code,
            context_data=context_data,
        )

        rendered = self._render_template(
            template.template_body,
            context_data,
        )


        return rendered

    # --------------------------------------------------------------
    # Artifact context validation (Stage 0 – critical)
    # --------------------------------------------------------------

    def _validate_artifact_context(
        self,
        artifact_code: str,
        context_data: Dict[str, Any],
    ) -> None:
        """
        Validate artifact context against frozen contract.

        Rules:
        - All required fields must be present
        - No unknown fields allowed
        - Optional fields allowed
        - Empty strings are treated as missing
        """

        contract = ARTIFACT_CONTEXT_CONTRACTS.get(artifact_code)

        if not contract:
            raise ValidationError(
                f"No artifact context contract defined for '{artifact_code}'"
            )

        required_fields = set(contract.get("required", []))
        optional_fields = set(contract.get("optional", []))
        allowed_fields = required_fields | optional_fields

        provided_fields = set(context_data.keys())

        # Missing required fields
        missing = {
            field for field in required_fields
            if field not in context_data
            or context_data[field] is None
            or context_data[field] == ""
        }


        if missing:
            raise ValidationError(
                f"Missing required fields for {artifact_code}: "
                f"{', '.join(sorted(missing))}"
            )

        # Unknown fields (strict!)
        unknown = provided_fields - allowed_fields
        if unknown:
            raise ValidationError(
                f"Unknown fields for {artifact_code}: "
                f"{', '.join(sorted(unknown))}"
            )

    # --------------------------------------------------------------
    # Validation & override hooks
    # --------------------------------------------------------------

    def validate_obligation(self, obligation_id: int) -> None:
        """
        Validate obligation completion.

        Placeholder for:
        - quorum checks
        - document presence
        - signature checks
        """
        # TODO: plug validator engine
        pass

    def override_obligation(
        self,
        obligation_id: int,
        user_id: int,
        reason: str,
    ) -> None:
        """
        Override obligation with audit trail.
        """

        self._governance_check(
            "onboarding.override",
            {"obligation_id": obligation_id, "user_id": user_id},
        )

        # TODO: write override record
        pass
    # --------------------------------------------------------------
    # Registrar submission (GUARDED ENTRY POINT)
    # --------------------------------------------------------------

    @transaction.atomic
    def submit_for_registration(self, society: Society) -> None:
        """
        Submit society for Registrar registration.

        This is the ONLY allowed entry point into the
        Registrar Submission flow.
        """

        if society is None:
            raise ValidationError(
                "No society found. Cannot submit for registration."
            )

        self._governance_check(
            "onboarding.submit_for_registration",
            {"society_id": society.id},
        )

        # Validate prereg completion
        if not is_preregistration_complete(society):
            raise ValidationError({
                "message": "Pre-registration onboarding is incomplete.",
                "blockers": preregistration_blockers(society),
            })

        # --------------------------------------------------
        # PREVENT DOUBLE SUBMISSION
        # --------------------------------------------------
        from statutory.models import RegistrarSubmission
        from statutory.preregistration.snapshot import preregistration_readiness_snapshot
        from django.utils import timezone

        if RegistrarSubmission.objects.filter(
            society=society,
            status="SUBMITTED"
        ).exists():
            raise ValidationError("Society already submitted to registrar.")

        # --------------------------------------------------
        # CAPTURE SNAPSHOT HASH (LEGAL RECORD)
        # --------------------------------------------------
        snapshot = preregistration_readiness_snapshot(society)

        RegistrarSubmission.objects.create(
            society=society,
            snapshot_hash=str(hash(str(snapshot))),
            submitted_at=timezone.now(),
            status="SUBMITTED",
        )

        # --------------------------------------------------
        # FUTURE LIFECYCLE HOOKS (INTENTIONALLY EMPTY)
        # --------------------------------------------------
        # TODO (Phase B):
        # - mark PRE_REGISTRATION stage complete
        # - freeze prereg obligations
        # - lock document uploads
        # - transition lifecycle state
        # - emit registrar.submission.initiated event

        return None


    # --------------------------------------------------------------
    # Stage progression
    # --------------------------------------------------------------

    def progress_stage(self, society: Society) -> None:
        """
        Progress to next legal stage if all mandatory obligations satisfied.
        """
        # TODO: compute completion state
        pass

    # --------------------------------------------------------------
    # Finalization
    # --------------------------------------------------------------

    @transaction.atomic
    def finalize_onboarding(self, society: Society) -> None:
        """
        Mark society as legally formed / registered.
        """

        self._governance_check(
            "onboarding.finalize",
            {"society_id": society.id},
        )

        # TODO:
        # - mark final stage complete
        # - assign chairman role
        # - emit onboarding.completed event
        pass

    def _initialize_finance_layer(self, society):
        """
        Seeds Chart of Accounts and creates opening AccountingPeriod.
        Idempotent.
        """

        # Prevent double initialization
        if society.chart_of_accounts.exists() and society.accounting_periods.exists():
            return

        from society.services import seed_default_coa_for_society
        from society.services import create_opening_accounting_period_for_society

        # Seed COA
        seed_default_coa_for_society(society=society)

        # Create first financial year
        create_opening_accounting_period_for_society(society=society)
        
    