# # Create SocietyConsent model 5.2.7 on 2026-03-13 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statutory', '0005_rename_mandatory_legalobligation_is_mandatory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocietyConsent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('consent_document', models.FileField(blank=True, null=True, upload_to='consent_letters/')),
                ('token', models.CharField(max_length=64, unique=True)),
                ('requested_at', models.DateTimeField(auto_now_add=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('flat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='society.flat')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='society.person')),
                ('society', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='society.society')),
            ],
            options={
                'unique_together': {('society', 'flat')},
            },
        ),
    ]
