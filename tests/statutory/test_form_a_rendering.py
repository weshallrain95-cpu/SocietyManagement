import pytest
from statutory.onboarding.engine import (
    StatutoryOnboardingEngine,
    ValidationError,
)

@pytest.mark.django_db
def test_form_a_renders_successfully_with_valid_context():
    engine = StatutoryOnboardingEngine()

    context = {
        "society_name": "Sunshine CHS",
        "society_address": "Andheri East, Mumbai",
        "society_type": "Cooperative Housing Society",
        "area_of_operation": "Mumbai Suburban",
        "first_meeting_date": "2025-01-15",
        "promoter_count": 12,
        "chief_promoter_name": "Rajesh Mehta",
        "chief_promoter_address": "Flat 12A",
        "chief_promoter_phone": "9876543210",
        "authorized_share_capital": 500000,
        "share_value": 10000,
        "bank_name": "SBI",
        "bank_branch": "Andheri East",
        "declaration_place": "Mumbai",
        "declaration_date": "2025-01-16",
        "chief_promoter_signature": "Rajesh Mehta",
    }

    rendered = engine._render_template(
        template_body="Name: {{ society_name }} | Address: {{ society_address }}",
        context_data=context,
        artifact_code="FORM_A_MH",
    )

    assert "Sunshine CHS" in rendered


@pytest.mark.django_db
def test_form_a_rejects_missing_required_fields():
    engine = StatutoryOnboardingEngine()

    with pytest.raises(ValidationError):
        engine._render_template(
            template_body="Name: {{ society_name }}",
            context_data={"society_name": "Test"},
            artifact_code="FORM_A_MH",
        )
