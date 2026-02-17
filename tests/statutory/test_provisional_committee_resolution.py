import pytest
from statutory.onboarding.engine import (
    StatutoryOnboardingEngine,
    ValidationError,
)

@pytest.mark.django_db
def test_provisional_committee_resolution_renders_with_valid_context():
    engine = StatutoryOnboardingEngine()

    context = {
        "society_name": "Green Meadows CHS",
        "meeting_date": "2025-01-15",
        "meeting_place": "Site Office",
        "resolution_number": "PMC-01",
        "chairman_name": "Amit Shah",
        "secretary_name": "Neha Kulkarni",
        "committee_members": [],
        "resolution_text": "Resolved to appoint PMC",
        "signatories": [],
    }

    rendered = engine._render_template(
        template_body="Resolution {{ resolution_number }} for {{ society_name }}",
        context_data=context,
        artifact_code="PROVISIONAL_COMMITTEE_RESOLUTION_MH",
    )

    assert "PMC-01" in rendered


@pytest.mark.django_db
def test_provisional_committee_resolution_rejects_missing_fields():
    engine = StatutoryOnboardingEngine()

    with pytest.raises(ValidationError):
        engine._render_template(
            template_body="Resolution {{ resolution_number }}",
            context_data={"society_name": "Test"},
            artifact_code="PROVISIONAL_COMMITTEE_RESOLUTION_MH",
        )
