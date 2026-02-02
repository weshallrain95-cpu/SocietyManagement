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
    # Entry point – Stage 0
    # --------------------------------------------------------------

    @transaction.atomic
    def start_onboarding(
        self,
        initiator_phone: str,
        society_data: Optional[Dict[str, Any]] = None,
        state_code: str = "MH",
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
        society = self._create_or_get_society_draft(society_data)

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
        self, society_data: Optional[Dict[str, Any]]
    ) -> Society:
        """
        Create minimal Society record if not present.
        """
        if not society_data:
            society_data = {"name": "Draft Society"}

        # TODO: smarter matching / dedupe logic
        society = Society.objects.create(**society_data)
        return society

    # --------------------------------------------------------------
    # Legal stage seeding
    # --------------------------------------------------------------

    def _seed_legal_stages(self, society: Society, state_code: str) -> None:
        """
        Attach LegalStage graph to society.
        """
        stages = LegalStage.objects.filter(state=state_code).order_by("sequence_order")

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
        Generate auto-filled legal artifact (bylaws, forms, letters).

        Returns rendered document (HTML / text / path).
        """

        obligation = LegalObligation.objects.get(id=obligation_id)
        template = LegalArtifactTemplate.objects.filter(
            legal_obligation=obligation
        ).first()

        if not template:
            raise ValidationError("No artifact template found")

        # TODO: render template_body with context_data
        return template.template_body

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
