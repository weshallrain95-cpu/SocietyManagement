from django.core.exceptions import ValidationError

from statutory.preregistration.status import (
    is_preregistration_complete,
    preregistration_blockers,
)
from society.models import Society


def preregistration_completion_response(society: Society) -> dict:
    """
    Ceremonial completion response for pre-registration onboarding.

    This function MUST:
    - Return a named success response when complete
    - Fail loudly and explainably when incomplete
    """

    if society is None:
        raise ValidationError(
            "No society found. Pre-registration cannot be completed."
        )

    if not is_preregistration_complete(society):
        raise ValidationError({
            "message": "Pre-registration onboarding is incomplete.",
            "blockers": preregistration_blockers(society),
        })

    return {
        "status": "PRE_REGISTRATION_COMPLETED",
        "message": "Pre-Registration Onboarding Completed Successfully",
        "registrar_ready": True,
    }
