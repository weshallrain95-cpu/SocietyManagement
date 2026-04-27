from datetime import date
import re
from statutory.document_engine.context_builder import build_template_context

from django.core.files.base import ContentFile
from django.utils import timezone

from statutory.models import (
    LegalArtifactTemplate,
    LegalObligation,
    SocietyLegalDocument,
    SocietyConsent,
)

from society.models import FlatOwner


# ---------------------------------------------------
# TEMPLATE RENDERER
# ---------------------------------------------------

class TemplateRenderer:

    PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")

    @staticmethod
    def extract_placeholders(template_body: str):
        return set(
            TemplateRenderer.PLACEHOLDER_PATTERN.findall(template_body)
        )

    @staticmethod
    def render(template_body: str, context: dict) -> str:

        required = TemplateRenderer.extract_placeholders(template_body)

        missing = [
            p for p in required
            if p not in context or context[p] in [None, ""]
        ]

        if missing:
            raise ValueError(
                f"Document generation blocked. Missing placeholders: {missing}"
            )

        rendered = template_body

        for key, value in context.items():
            rendered = re.sub(
                r"{{\s*" + key + r"\s*}}",
                str(value),
                rendered
            )

        return rendered


# ---------------------------------------------------
# DOCUMENT GENERATOR
# ---------------------------------------------------

class DocumentGenerator:
    """
    Central engine for generating statutory artifacts.
    """

    # ---------------------------------------------
    # Governance Hook Guardrails
    # ---------------------------------------------

    REQUIRED_HOOKS = {

        "PROVISIONAL_COMMITTEE_RESOLUTION_MH": [
            "resolution_number",
            "meeting_date",
            "meeting_place",
            "chief_promoter_name",
            "committee_members",
            "signatories",
            "project_name",
            "project_address",
        ]

    }

    FORM_A_REQUIRED_FIELDS = [
        "registrar_district",
        "society_name",
        "society_address",
        "society_type",
        "area_of_operation",
        "promoter_count",
        "chief_promoter_name",
        "chief_promoter_address",
        "chief_promoter_phone",
        "authorized_share_capital",
        "share_value",
        "bank_name",
        "bank_branch",
        "first_meeting_date",
        "declaration_place",
        "declaration_date",
        "promoter_member_table"
    ]


    # ---------------------------------------------
    # Context Builder
    # ---------------------------------------------

    @staticmethod
    def build_context(society, extra=None):

        # 🔹 Build full context using new engine
        context = build_template_context(
        society=society,
        ux_payload=extra or {}
    )

        # 🔹 Add system defaults (if needed)
        context["date"] = date.today()
        context["state"] = getattr(society, "state_code", "")

        return context


    # ---------------------------------------------
    # Hook Validator
    # ---------------------------------------------

    @staticmethod
    def validate_hooks(artifact_code, context):

        required = DocumentGenerator.REQUIRED_HOOKS.get(
            artifact_code,
            []
        )

        missing = [
            f for f in required
            if f not in context or context[f] in [None, ""]
        ]

        if missing:
            raise ValueError(
                f"Legal guardrail triggered. Missing hooks: {missing}"
            )


    # ---------------------------------------------
    # FORM A Guardrails
    # ---------------------------------------------

    @staticmethod
    def validate_form_a(context):

        missing = [
            f for f in DocumentGenerator.FORM_A_REQUIRED_FIELDS
            if f not in context or context[f] in [None, ""]
        ]

        if missing:
            raise ValueError(
                f"Form A blocked. Missing fields: {missing}"
            )

        if int(context["promoter_count"]) < 10:
            raise ValueError(
                "Registrar requirement: Minimum 10 promoter members required"
            )


    # ---------------------------------------------
    # Core Generator
    # ---------------------------------------------

    @staticmethod
    def generate_document(society, artifact_code, extra_context=None):

        try:
            template = LegalArtifactTemplate.objects.get(
                artifact_code=artifact_code
            )
        except LegalArtifactTemplate.DoesNotExist:
            raise ValueError(
                f"No template found for artifact: {artifact_code}"
            )

        context = DocumentGenerator.build_context(
            society,
            extra_context
        )

        # Guardrails
        DocumentGenerator.validate_hooks(
            artifact_code,
            context
        )

        if artifact_code == "FORM_A_MH":
            DocumentGenerator.validate_form_a(context)

        rendered_text = TemplateRenderer.render(
            template.template_body,
            context
        )

        file_name = f"{artifact_code}_{society.id}.txt"

        document, _ = SocietyLegalDocument.objects.get_or_create(
            society=society,
            template=template,
            defaults={"status": "GENERATED"}
        )

        document.file.save(
            file_name,
            ContentFile(rendered_text),
            save=False
        )

        document.status = "GENERATED"
        document.save()

        return document


    # ---------------------------------------------
    # Consent Letter Generator
    # ---------------------------------------------

    @staticmethod
    def generate_consent_letters(society):

        template = LegalArtifactTemplate.objects.get(
            artifact_code="PROMOTER_CONSENT_LETTER_MH"
        )

        consents = SocietyConsent.objects.filter(
            society=society
        ).select_related("flat", "owner")

        letters = []

        for consent in consents:

            context = {
                "society_name": society.name,
                "project_name": society.name,
                "project_address": society.address,
                "flat_number": consent.flat.flat_number,
                "owner_name": consent.owner.full_name,
                "token": consent.token
            }

            rendered = TemplateRenderer.render(
                template.template_body,
                context
            )

            letters.append(rendered)

        # combine all letters
        combined_document = "\n\n\n-----------------------------\n\n\n".join(letters)

        filename = f"CONSENT_LETTERS_{society.id}.txt"

        document, created = SocietyLegalDocument.objects.get_or_create(
            society=society,
            template=template,
            defaults={"status": "GENERATED"}
        )

        document.file.save(
            filename,
            ContentFile(combined_document),
            save=True
        )

        return document


    # ---------------------------------------------
    # Generate For Obligation
    # ---------------------------------------------

    @staticmethod
    def generate_for_obligation(society, obligation: LegalObligation):

        documents = []

        templates = obligation.artifact_templates.all()

        for template in templates:

            doc = DocumentGenerator.generate_document(
                society,
                template.artifact_code
            )

            documents.append(doc)

        return documents