from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0047_coa_upgrade_v1'),
    ]

    operations = [
        migrations.AddField(
            model_name='society',
            name='registration_certificate',
            field=models.FileField(
                upload_to='registration_docs/',
                null=True,
                blank=True
            ),
        ),
        migrations.AddField(
            model_name='society',
            name='oc_certificate',
            field=models.FileField(
                upload_to='registration_docs/',
                null=True,
                blank=True
            ),
        ),
    ]