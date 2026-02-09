from django.db import migrations


def seed_stage0_maharashtra(apps, schema_editor):
    LegalStage = apps.get_model("statutory", "LegalStage")
    LegalObligation = apps.get_model("statutory", "LegalObligation")
    LegalChecklistItem = apps.get_model("statutory", "LegalChecklistItem")
    LegalArtifactTemplate = apps.get_model("statutory", "LegalArtifactTemplate")
    State = apps.get_model("statutory", "State")

    # Fetch Maharashtra state
    mh_state = State.objects.get(code="MH")

    # -----------------------------
    # Stage 0 — Pre-registration
    # -----------------------------
    stage0, _ = LegalStage.objects.get_or_create(
        name="Society Formation & Registration (Pre-Registration)",
        state=mh_state,
        defaults={
            "sequence_order": 0,
            "description": "Guided formation of a cooperative housing society before registration",
            "is_mandatory": True,
        },
    )

    obligations = [
        {
            "title": "Collect minimum 60% consent from flat purchasers",
            "artifact": None,
        },
        {
            "title": "Form provisional managing committee",
            "artifact": "RESOLUTION_PROVISIONAL_COMMITTEE",
        },
        {
            "title": "Collect builder-provided documents",
            "artifact": "BUILDER_DOCUMENT_SET",
        },
        {
            "title": "Prepare proposed society name",
            "artifact": None,
        },
        {
            "title": "Draft proposed society by-laws",
            "artifact": "BYLAW_DRAFT",
        },
        {
            "title": "Open provisional society bank account",
            "artifact": "BANK_ACCOUNT_LETTER",
        },
        {
            "title": "Prepare registration application (Form A)",
            "artifact": "FORM_A",
        },
        {
            "title": "Conduct first general meeting",
            "artifact": "FIRST_AGM_MINUTES",
        },
        {
            "title": "Submit registration to registrar",
            "artifact": "REGISTRATION_ACKNOWLEDGEMENT",
        },
    ]

    for item in obligations:
        obligation, _ = LegalObligation.objects.get_or_create(
            legal_stage=stage0,
            title=item["title"],
            defaults={
                "description": item["title"],
                "mandatory": True,
                "reference_law": "MCS Act, 1960 / MCS Rules, 1961",
            },
        )

        LegalChecklistItem.objects.get_or_create(
            legal_obligation=obligation,
            description=f"Complete: {item['title']}",
            mandatory=True,
        )

        if item["artifact"]:
            LegalArtifactTemplate.objects.get_or_create(
                legal_obligation=obligation,
                artifact_type=item["artifact"],
                defaults={
                    "template_body": f"Template for {item['title']} — placeholders only",
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("statutory", "0006_alter_societylegaldocument_status_shareownership"),
    ]

    operations = [
        migrations.RunPython(seed_stage0_maharashtra),
    ]
