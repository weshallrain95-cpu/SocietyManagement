from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('society', '0044_add_flat_to_ledgerentryv2'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # =========================
        # Legacy Ledger Preservation
        # =========================
        migrations.CreateModel(
            name='LedgerEntryV1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=14)),
                ('description', models.TextField()),
                ('entry_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('source_type', models.CharField(blank=True, max_length=50)),
                ('source_ref', models.CharField(blank=True, max_length=100)),
                ('credit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='legacy_v1_credits', to='society.chartofaccount')),
                ('debit_account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='legacy_v1_debits', to='society.chartofaccount')),
                ('flat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='society.flat')),
                ('society', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='legacy_v1_entries', to='society.society')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['entry_date', 'id'],
            },
        ),

        # =========================
        # BankAccount (New System)
        # =========================
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('bank_name', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=50)),
                ('ifsc', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chart_account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bank_account', to='society.chartofaccount')),
                ('society', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bank_accounts', to='society.society')),
            ],
            options={
                'unique_together': {('society', 'account_number')},
            },
        ),
    ]