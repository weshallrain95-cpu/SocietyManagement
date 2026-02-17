import pytest
from statutory.onboarding.engine import (
    StatutoryOnboardingEngine,
    ValidationError,
)

@pytest.mark.django_db
def test_bylaw_draft_renders_with_valid_context():
    engine = StatutoryOnboardingEngine()

    context = {
        "society_name": "Green Meadows CHS Ltd.",
        "registered_address": "Wakad, Pune",
        "district": "Pune",
        "promoter_name": "ABC Developers",
        "total_flats": 120,
        "adoption_date": "2025-01-20",
    }

    rendered = engine._render_template(
        template_body="Bye-laws of {{ society_name }}",
        context_data=context,
        artifact_code="BYLAW_DRAFT_MH",
    )

    assert "Green Meadows" in rendered


@pytest.mark.django_db
def test_bylaw_draft_rejects_missing_required_fields():
    engine = StatutoryOnboardingEngine()

    with pytest.raises(ValidationError):
        engine._render_template(
            template_body="Bye-laws of {{ society_name }}",
            context_data={"society_name": "Test"},
            artifact_code="BYLAW_DRAFT_MH",
        )
