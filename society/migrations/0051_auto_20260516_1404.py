from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0050_add_treasury_role_and_bank_address'),
    ]

    operations = [

        migrations.AlterField(
            model_name='memberreceivable',
            name='bill',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name='receivable',
                to='society.flatmaintenancebill',
            ),
        ),

        migrations.AddField(
            model_name='memberreceivable',
            name='source_reference',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
            ),
        ),

        migrations.AddField(
            model_name='memberreceivable',
            name='source_type',
            field=models.CharField(
                default='BILL',
                max_length=30,
            ),
        ),

    ]