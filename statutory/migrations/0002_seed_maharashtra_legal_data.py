from django.db import migrations


def seed_maharashtra_legal_data(apps, schema_editor):
    State = apps.get_model('statutory', 'State')
    LegalStage = apps.get_model('statutory', 'LegalStage')
    LegalObligation = apps.get_model('statutory', 'LegalObligation')

    # Create Maharashtra state
    mh, _ = State.objects.get_or_create(
        code='MH',
        defaults={'name': 'Maharashtra'}
    )

    stages = [
        (1, "Society Formation Consent"),
        (2, "Provisional Committee Formation"),
        (3, "Document Collection from Builder"),
        (4, "Application for Registration"),
        (5, "First General Meeting"),
        (6, "Election of Managing Committee"),
        (7, "Bank Account, PAN & Statutory Registers"),
    ]

    stage_map = {}

    for order, name in stages:
        stage = LegalStage.objects.create(
            state=mh,
            name=name,
            sequence_order=order,
            is_mandatory=True
        )
        stage_map[name] = stage

    LegalObligation.objects.bulk_create([
        LegalObligation(
            legal_stage=stage_map["Society Formation Consent"],
            title="Collect consent letters from members",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["Provisional Committee Formation"],
            title="Form provisional managing committee",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["Document Collection from Builder"],
            title="Collect conveyance deed and approved plans",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["Application for Registration"],
            title="Submit registration application (Form A)",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["First General Meeting"],
            title="Conduct first general meeting with quorum",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["Election of Managing Committee"],
            title="Conduct election of managing committee",
            mandatory=True
        ),
        LegalObligation(
            legal_stage=stage_map["Bank Account, PAN & Statutory Registers"],
            title="Open bank account and apply for PAN",
            mandatory=True
        ),
    ])


def reverse_seed(apps, schema_editor):
    State = apps.get_model('statutory', 'State')
    State.objects.filter(code='MH').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('statutory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_maharashtra_legal_data, reverse_seed),
    ]
