import pytest
from statutory.onboarding.engine import (
    StatutoryOnboardingEngine,
    ValidationError,
)

def test_engine_imports_cleanly():
    engine = StatutoryOnboardingEngine()
    assert engine is not None


def test_render_template_basic_substitution():
    engine = StatutoryOnboardingEngine()

    template = "Society: {{ society_name }} | Chairman: {{ chairman_name }}"
    context = {
        "society_name": "Sunrise CHS",
        "chairman_name": "Amit Patil",
        "meeting_date": "2025-01-01",
        "meeting_place": "Site Office",
        "resolution_number": "PMC-01",
        "secretary_name": "Neha Kulkarni",
        "committee_members": [],
        "resolution_text": "Test",
        "signatories": [],
    }

    rendered = engine._render_template(
        template,
        context_data=context,
        artifact_code="PROVISIONAL_COMMITTEE_RESOLUTION_MH",
    )

    assert "Sunrise CHS" in rendered
    assert "Amit Patil" in rendered


def test_artifact_context_validation_rejects_missing_fields():
    engine = StatutoryOnboardingEngine()

    incomplete_context = {
        "society_name": "Test Society"
    }

    with pytest.raises(ValidationError):
        engine._validate_artifact_context(
            "FORM_A_MH",
            incomplete_context,
        )
