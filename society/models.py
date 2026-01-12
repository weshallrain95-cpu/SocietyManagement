from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User


class Society(models.Model):
    """
    Canonical Society master.
    Represents one legally registered housing society.
    """

    # -----------------------------
    # Core Identity
    # -----------------------------
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)

    # -----------------------------
    # Legal / Registrar Identity
    # -----------------------------
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Official society registration number issued by Registrar"
    )

    registration_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of registration with Registrar"
    )

    registrar_office = models.CharField(
        max_length=255,
        blank=True,
        help_text="Registrar office / ward / zone"
    )

    LEGAL_STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("IN_PROCESS", "In Process"),
        ("LEGALLY_COMPLETE", "Legally Complete"),
    ]

    legal_status = models.CharField(
        max_length=30,
        choices=LEGAL_STATUS_CHOICES,
        default="DRAFT",
    )

    # -----------------------------
    # Metadata
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["registration_number"],
                name="unique_society_registration_number"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.registration_number})"

from django.db import models

class Flat(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="flats",
    )

    flat_number = models.CharField(
        max_length=20,
        help_text="Flat number as per society records (e.g. A-101, 1203)"
    )

    wing = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Wing / building identifier (if applicable)"
    )

    floor = models.IntegerField(
        blank=True,
        null=True,
        help_text="Floor number"
    )

    carpet_area_sqft = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Carpet area in square feet"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this flat is active (not merged / demolished)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("society", "flat_number")
        ordering = ["flat_number"]

    def __str__(self):
        return f"{self.flat_number} ({self.society.name})"

class FlatOwnership(models.Model):
    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        related_name="ownerships",
    )

    acquired_on = models.DateField()
    relinquished_on = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-acquired_on"]
        constraints = [
            models.UniqueConstraint(
                fields=["flat"],
                condition=Q(is_active=True),
                name="one_active_ownership_per_flat",
            )
        ]

    def __str__(self):
        status = "ACTIVE" if self.is_active else "CLOSED"
        return f"{self.flat} [{status}]"


from django.conf import settings
from django.db import models

class FlatOccupancy(models.Model):
    flat = models.OneToOneField(
        "Flat",
        on_delete=models.CASCADE,
        related_name="occupancy",
    )

    OCCUPANCY_TYPE_CHOICES = [
        ("SELF", "Self Occupied"),
        ("RENTED", "Rented / Leave & License"),
        ("FAMILY", "Occupied by Family"),
        ("VACANT", "Vacant / Locked"),
        ("CORPORATE", "Corporate Occupancy"),
    ]

    occupancy_type = models.CharField(
        max_length=20,
        choices=OCCUPANCY_TYPE_CHOICES,
        default="SELF",
    )

    declared_on = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.flat} – {self.occupancy_type}"
class MaintenanceAccount(models.Model):
    flat = models.OneToOneField(
        "Flat",
        on_delete=models.CASCADE,
        related_name="maintenance_account",
    )

    outstanding_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    last_paid_on = models.DateField(null=True, blank=True)
    balance_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    last_billed_on = models.DateField(null=True, blank=True)

    is_defaulter = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.flat} – Due: {self.balance_due}"
    STATUS_CHOICES = [
        ("CLEAR", "No Dues"),
        ("OVERDUE", "Overdue"),
        ("NOTICE_SENT", "Notice Issued"),
        ("RESOLUTION_PASSED", "Resolution Passed"),
        ("LEGAL", "Legal Recovery"),
    ]

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="CLEAR",
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flat} – {self.status}"

class FlatOwner(models.Model):
    ownership = models.ForeignKey(
        "society.FlatOwnership",
        on_delete=models.CASCADE,
        related_name="owners",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Linked user account (if individual)",
    )

    legal_entity_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Company / Trust / Entity name (if applicable)",
    )

    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Ownership percentage (e.g. 50.00)",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False)
                    | models.Q(legal_entity_name__isnull=False)
                ),
                name="flatowner_requires_person_or_entity",
            )
        ]

    def __str__(self):
        return self.user.get_full_name() if self.user else self.legal_entity_name
class Amenity(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="amenities",
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    is_chargeable = models.BooleanField(default=False)

    # Future-proofing (not used yet)
    charge_type = models.CharField(
        max_length=20,
        choices=[
            ("PER_USE", "Per Use"),
            ("MONTHLY", "Monthly"),
            ("ANNUAL", "Annual"),
        ],
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("society", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({'Paid' if self.is_chargeable else 'Free'})"
class ParkingSlot(models.Model):
    PARKING_TYPE_CHOICES = [
        ("CAR", "Car"),
        ("BIKE", "Bike"),
        ("VISITOR", "Visitor"),
    ]

    ALLOCATION_TYPE_CHOICES = [
        ("FLAT", "Flat Allotted"),
        ("MEMBER", "Member Allotted"),
        ("COMMON", "Common Use"),
    ]

    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name="parking_slots",
    )

    slot_number = models.CharField(max_length=20)

    parking_type = models.CharField(
        max_length=20,
        choices=PARKING_TYPE_CHOICES,
    )

    allocation_type = models.CharField(
        max_length=20,
        choices=ALLOCATION_TYPE_CHOICES,
        default="COMMON",
    )

    is_chargeable = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.society.name} - {self.slot_number}"
class ParkingAllocation(models.Model):
    parking_slot = models.ForeignKey(
        ParkingSlot,
        on_delete=models.CASCADE,
        related_name="allocations",
    )

    flat = models.ForeignKey(
        Flat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parking_allocations",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parking_allocations",
    )

    allocated_on = models.DateField()
    released_on = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.parking_slot} → {self.flat or self.user}"
class Amenity(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="amenities",
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_mandatory = models.BooleanField(
        default=False,
        help_text="Mandatory for all flats",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("society", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.society.name} – {self.name}"
class AmenityChargeRule(models.Model):
    CHARGE_TYPE_CHOICES = [
        ("FREE", "Free"),
        ("FIXED", "Fixed Monthly"),
        ("PER_USE", "Per Use"),
        ("PER_FLAT", "Per Flat"),
    ]

    amenity = models.OneToOneField(
        Amenity,
        on_delete=models.CASCADE,
        related_name="charge_rule",
    )

    charge_type = models.CharField(
        max_length=20,
        choices=CHARGE_TYPE_CHOICES,
        default="FREE",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly or per-use amount",
    )

    effective_from = models.DateField()

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["effective_from"]

    def __str__(self):
        return f"{self.amenity.name} – {self.charge_type}"
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Flat)
def create_flat_defaults(sender, instance, created, **kwargs):
    if created:
        FlatOccupancy.objects.get_or_create(flat=instance)
        MaintenanceAccount.objects.get_or_create(flat=instance)
class ChargeType(models.Model):
    """
    Defines types of charges a society can levy.
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    # Examples:
    # SERVICE_CHARGE, NON_OCCUPANCY_CHARGE, PARKING_CHARGE

    is_percentage = models.BooleanField(
        default=False,
        help_text="If true, charge is a percentage-based calculation",
    )

    max_percentage_cap = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum allowed percentage (e.g. 10.00 for NOC)",
    )

    applies_on = models.CharField(
        max_length=50,
        choices=[
            ("SERVICE_CHARGES", "Service Charges"),
            ("MAINTENANCE", "Maintenance"),
            ("NONE", "Not Applicable"),
        ],
        default="NONE",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
class SocietyChargeRule(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="charge_rules",
    )

    charge_type = models.ForeignKey(
        ChargeType,
        on_delete=models.PROTECT,
    )

    rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Percentage or flat amount depending on charge type",
    )

    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("society", "charge_type", "effective_from")

    def __str__(self):
        return f"{self.society} – {self.charge_type}"
class MaintenanceBill(models.Model):
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name="maintenance_bills",
    )

    billing_month = models.DateField(
        help_text="First day of the billing month"
    )

    generated_on = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        unique_together = ("society", "billing_month")
        ordering = ["-billing_month"]

    def __str__(self):
        return f"{self.society.name} — {self.billing_month}"
class FlatMaintenanceBill(models.Model):
    bill = models.ForeignKey(
        MaintenanceBill,
        on_delete=models.CASCADE,
        related_name="flat_bills",
    )

    flat = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
    )

    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    non_occupancy_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    total_payable = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("bill", "flat")

    def __str__(self):
        return f"{self.flat} — {self.total_payable}"

from decimal import Decimal
from django.utils import timezone

class Payment(models.Model):
    PAYMENT_MODES = [
        ("CASH", "Cash"),
        ("CHEQUE", "Cheque"),
        ("UPI", "UPI"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("ONLINE", "Online Gateway"),
    ]

    STATUS_CHOICES = [
        ("RECEIVED", "Received"),
        ("CLEARED", "Cleared"),
        ("BOUNCED", "Bounced"),
        ("REVERSED", "Reversed"),
    ]

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="payments",
    )

    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        related_name="payments",
    )

    bill = models.ForeignKey(
        "society.MaintenanceBill",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        help_text="Null if advance or miscellaneous payment",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Cheque no / UTR / Txn ID",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="RECEIVED",
    )

    received_on = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_on", "-created_at"]

    def __str__(self):
        return f"{self.flat} ₹{self.amount} ({self.payment_mode})"


class SocietyRule(models.Model):
    RULE_TYPES = [
        ("INTEREST", "Interest"),
        ("NON_OCCUPANCY", "Non Occupancy Charge"),
        ("LATE_FEE", "Late Fee"),
    ]

    society = models.ForeignKey("Society", on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=30, choices=RULE_TYPES)

    rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Percentage rate (e.g. 10.00 for 10%)",
    )

    cap_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum cap if applicable",
    )

    applies_after_days = models.PositiveIntegerField(
        default=0,
        help_text="Grace period before rule applies",
    )

    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

from django.db import models

class NoticeLog(models.Model):
    NOTICE_TYPES = [
        ("REMINDER", "Reminder"),
        ("DEMAND", "Demand"),
        ("FINAL", "Final Notice"),
        ("LEGAL", "Legal Notice"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="notices",
    )

    flat = models.ForeignKey(
        "Flat",
        on_delete=models.CASCADE,
        related_name="notices",
    )

    notice_type = models.CharField(
        max_length=20,
        choices=NOTICE_TYPES,
    )

    outstanding_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    interest_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    reference_period = models.CharField(
        max_length=50,
    )

    notes = models.TextField(blank=True)

    generated_on = models.DateField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_payable(self):
        return self.outstanding_amount + self.interest_amount

    def __str__(self):
        return f"{self.notice_type} | Flat {self.flat} | ₹{self.total_payable}"


    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.notice_type} | Flat {self.flat} | ₹{self.outstanding_amount}"

    interest_amount = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0,
)

total_payable = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    default=0,
)
# society/models.py

class RecoveryStage(models.TextChoices):
    NONE = "NONE", "No Recovery"
    REMINDER = "REMINDER", "Reminder Issued"
    DEMAND = "DEMAND", "Demand Notice"
    FINAL = "FINAL", "Final Notice"
    REGISTRAR = "REGISTRAR", "Filed with Registrar"
    LEGAL = "LEGAL", "Legal Proceedings"
    CLOSED = "CLOSED", "Recovered / Closed"
class FlatRecoveryStatus(models.Model):
    flat = models.OneToOneField(
        "Flat",
        on_delete=models.CASCADE,
        related_name="recovery_status",
    )

    stage = models.CharField(
        max_length=20,
        choices=RecoveryStage.choices,
        default=RecoveryStage.NONE,
    )

    outstanding_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    last_action_on = models.DateField(auto_now=True)

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.flat} | {self.stage}"
class RecoveryActionLog(models.Model):
    flat = models.ForeignKey(
        "Flat",
        on_delete=models.CASCADE,
        related_name="recovery_actions",
    )

    stage = models.CharField(
        max_length=20,
        choices=RecoveryStage.choices,
    )

    action_date = models.DateField(auto_now_add=True)

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Notice number / Registrar file no / etc",
    )

    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.flat} → {self.stage}"
# society/models.py

from django.db import models

class ChartOfAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("ASSET", "Asset"),
        ("LIABILITY", "Liability"),
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
        ("EQUITY", "Equity"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="chart_of_accounts",
    )

    code = models.CharField(
        max_length=20,
        help_text="Short account code (e.g. MAINT, BANK, SINKFUND)",
    )

    name = models.CharField(
        max_length=255,
        help_text="Account name (e.g. Maintenance Charges)",
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("society", "code")
        ordering = ["account_type", "code"]

    def __str__(self):
        return f"{self.code} - {self.name}"
        def can_be_deleted(self):
            return not self.ledger_entries.exists()

class ChartOfAccount(models.Model):
    society = models.ForeignKey(
        Society,
        on_delete=models.CASCADE,
        related_name="chart_of_accounts",
    )

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=20,
        choices=[
            ("ASSET", "Asset"),
            ("LIABILITY", "Liability"),
            ("INCOME", "Income"),
            ("EXPENSE", "Expense"),
            ("RESERVE", "Reserve"),
        ],
    )

    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    is_system = models.BooleanField(
        default=False,
        help_text="System-generated account (do not delete)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("society", "code")

    def __str__(self):
        return f"{self.code} - {self.name}"

from django.db import models
from decimal import Decimal
from django.utils import timezone

class LedgerEntry(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="ledger_entries",
    )

    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    debit_account = models.ForeignKey(
        "society.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="debit_entries",
        null=True,   # TEMPORARY
        blank=True,
    )

    credit_account = models.ForeignKey(
        "society.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="credit_entries",
        null=True,   # TEMPORARY
        blank=True,
    )

    debit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    description = models.TextField()
    entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["entry_date", "id"]
from django.conf import settings

class LedgerEntry(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="ledger_entries",
    )

    flat = models.ForeignKey(
        "society.Flat",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    debit_account = models.ForeignKey(
        "society.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="debit_entries",
    )

    credit_account = models.ForeignKey(
        "society.ChartOfAccount",
        on_delete=models.PROTECT,
        related_name="credit_entries",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    description = models.TextField()
    entry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔐 AUDIT FIELDS (NEW)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="User who created this entry",
    )

    source_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="BILL / PAYMENT / ADJUSTMENT / OPENING",
    )

    source_ref = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference ID",
    )

    class Meta:
        ordering = ["entry_date", "id"]

    def __str__(self):
        return f"{self.entry_date} | {self.amount}"

# society/models.py
from society.constants import TransactionType

class TransactionRule(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="transaction_rules",
    )

    transaction_type = models.CharField(
        max_length=50,
        choices=[(t.value, t.value) for t in TransactionType],
    )

    debit_account_code = models.CharField(max_length=20)
    credit_account_code = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)

    from django.utils import timezone

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    class Meta:
        unique_together = ("society", "transaction_type")

    def __str__(self):
        return (
            f"{self.transaction_type} → "
            f"D:{self.debit_account_code} "
            f"C:{self.credit_account_code}"
        )
from django.core.exceptions import ValidationError
from society.models import ChartOfAccount

def clean(self):
    if self.debit_account_code == self.credit_account_code:
        raise ValidationError("Debit and Credit accounts cannot be the same.")

    if not ChartOfAccount.objects.filter(
        society=self.society, code=self.debit_account_code
    ).exists():
        raise ValidationError(f"Debit account {self.debit_account_code} not found.")

    if not ChartOfAccount.objects.filter(
        society=self.society, code=self.credit_account_code
    ).exists():
        raise ValidationError(f"Credit account {self.credit_account_code} not found.")
def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
class AccountingPeriod(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="accounting_periods",
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        unique_together = ("society", "start_date", "end_date")
        ordering = ["-start_date"]

    def __str__(self):
        status = "CLOSED" if self.is_closed else "OPEN"
        return f"{self.start_date} → {self.end_date} ({status})"

class PendingTransaction(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="pending_transactions",
    )

    transaction_type = models.CharField(
        max_length=50,
        choices=[(t.value, t.value) for t in TransactionType],
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)

    description = models.TextField()

    entry_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
    )

    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="transactions_created",
    )

    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions_approved",
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
