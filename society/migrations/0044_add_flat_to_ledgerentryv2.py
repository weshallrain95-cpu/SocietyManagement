from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0043_transaction_ledgerentryv2'),
    ]

    operations = [
        migrations.AddField(
            model_name='ledgerentryv2',
            name='flat',
            field=models.ForeignKey(
                to='society.flat',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='ledger_entries_v2',
            ),
        ),
    ]