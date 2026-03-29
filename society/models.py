from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from core.managers.society_manager import SocietyManager


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

    onboarding_stage = models.CharField(
        max_length=50,
        choices=[
            ("STRUCTURE_PENDING", "Structure Pending"),
            ("STRUCTURE_CREATED", "Structure Created"),
            ("OWNERSHIP_PENDING", "Ownership Pending"),
            ("ONBOARDING_COMPLETE", "Onboarding Complete"),
        ],
        default="STRUCTURE_PENDING"
    )
    # -----------------------------
    # Legal / Registrar Identity
    # -----------------------------
    registration_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
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
    # -----------------------------
    # Legal Jurisdiction (NEW)
    # -----------------------------
    state_code = models.CharField(
        max_length=10,
        default="MH",
        help_text="Legal jurisdiction state code (MH, KA, DL, etc.)"
    )
    
    district = models.CharField(max_length=120, null=True, blank=True)

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

class Wing(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="wings",
    )

    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = SocietyManager()
    
    class Meta:
        unique_together = ("society", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.society.name} - Wing {self.name}"

class Floor(models.Model):
    wing = models.ForeignKey(
        "society.Wing",
        on_delete=models.CASCADE,
        related_name="floors",
    )

    number = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wing", "number")
        ordering = ["number"]

    def __str__(self):
        return f"{self.wing} - Floor {self.number}"

# ==========================================================
# SOCIETY OFFICE BEARER (Governance Identity Layer)
# ==========================================================

class SocietyOfficeBearer(models.Model):
    """
    Canonical governance identity for a society.
    """

    ROLE_CHOICES = (
        ("CHAIRMAN", "Chairman"),
        ("SECRETARY", "Secretary"),
        ("TREASURER", "Treasurer"),
        ("COMMITTEE_MEMBER", "Committee Member"),
    )

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="office_bearers",
    )

    committee_membership_ref = models.ForeignKey(
        "society.CommitteeMembership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legacy_office_bearers",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="society_roles",
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        db_index=True,
    )

    appointed_on = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the role was assigned",
    )

    term_end = models.DateField(
        null=True,
        blank=True,
        help_text="End of office term",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-appointed_on", "-created_at"]
        indexes = [
            models.Index(fields=["society", "role", "is_active"]),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        leadership_roles = {"CHAIRMAN", "SECRETARY", "TREASURER"}

        # Leadership must be committee-backed
        if self.role in leadership_roles and not self.committee_membership_ref:
            raise ValidationError(
                f"{self.role} must be linked to an active CommitteeMembership."
            )

        if self.committee_membership_ref:

            # Same society enforcement
            if self.committee_membership_ref.society_id != self.society_id:
                raise ValidationError(
                    "Committee membership must belong to the same society."
                )

            # Active membership enforcement
            if not self.committee_membership_ref.is_active:
                raise ValidationError(
                    "Committee membership must be active."
                )

            # Term validity enforcement
            today = timezone.now().date()
            if not (
                self.committee_membership_ref.elected_on
                <= today
                <= self.committee_membership_ref.term_end
            ):
                raise ValidationError(
                    "Committee membership term is not currently valid."
                )

            # Identity binding enforcement
            member_person = self.committee_membership_ref.member.person

            if not member_person.user:
                raise ValidationError(
                    "Committee member's Person record must be linked to a User."
                )

            if self.user != member_person.user:
                raise ValidationError(
                    "OfficeBearer user must match Committee Member's linked User."
                )

    def __str__(self):
        return f"{self.user} — {self.role} — {self.society.name}"


from django.db import models


class Flat(models.Model):

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="flats",
    )

    # -----------------------------
    # Identity
    # -----------------------------
    flat_number = models.CharField(
        max_length=20,
        help_text="Flat number as per society records (e.g. A-101, 1203)",
    )

    wing = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Wing / building identifier (legacy support)",
    )

    floor = models.IntegerField(
        blank=True,
        null=True,
        help_text="Floor number (legacy support)",
    )

    # -----------------------------
    # Canonical Structure Links
    # -----------------------------
    wing_ref = models.ForeignKey(
        "society.Wing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flat_records",
    )

    floor_ref = models.ForeignKey(
        "society.Floor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flat_records",
    )

    # -----------------------------
    # Flat Configuration
    # -----------------------------
    flat_type = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Flat configuration such as 1BHK, 2BHK, 3BHK",
    )

    carpet_area_sqft = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Carpet area in square feet",
    )

    # -----------------------------
    # Status
    # -----------------------------
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this flat is active (not merged / demolished)",
    )

    # -----------------------------
    # Audit
    # -----------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SocietyManager()

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
    """
    Represents an owner of a flat.

    Ownership is linked to a FlatOwnership record so that
    ownership history (resale, transfer, inheritance) can
    be preserved over time.
    """

    ownership = models.ForeignKey(
        "society.FlatOwnership",
        on_delete=models.CASCADE,
        related_name="owners",
    )

    person = models.ForeignKey(
        "society.Person",
        on_delete=models.CASCADE,
        related_name="flat_ownerships",
        null=True,
        blank=True,
        help_text="Individual person owner (if applicable)",
    )

    legal_entity_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Company / Trust / Legal entity owner (if applicable)",
    )

    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Ownership percentage (must total 100% per flat)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(person__isnull=False)
                    | models.Q(legal_entity_name__isnull=False)
                ),
                name="flatowner_requires_person_or_entity",
            ),
            models.UniqueConstraint(
                fields=["ownership", "person"],
                name="unique_owner_per_flat",
            ),
        ]

    def __str__(self):
        if self.person:
            return f"{self.person.full_name} ({self.ownership.flat.flat_number})"

        return f"{self.legal_entity_name} ({self.ownership.flat.flat_number})"

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

    objects = SocietyManager()

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

    objects = SocietyManager()

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

    objects = SocietyManager()

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

    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    non_occupancy_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_payable = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("bill", "flat")

    def __str__(self):
        return f"{self.flat} — {self.total_payable}"

class FlatMaintenanceBillLine(models.Model):

    bill = models.ForeignKey(
        "FlatMaintenanceBill",
        on_delete=models.CASCADE,
        related_name="lines"
    )

    charge_code = models.CharField(max_length=50)

    charge_name = models.CharField(max_length=255)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.charge_name} - {self.amount}"


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

    objects = SocietyManager()

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

class AccountGroup(models.Model):

    CATEGORY_CHOICES = [
        ("ASSET", "Asset"),
        ("LIABILITY", "Liability"),
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    is_system = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# society/models.py

from django.db import models

class ChartOfAccount(models.Model):

    ACCOUNT_TYPE_CHOICES = [
        ("ASSET", "Asset"),
        ("LIABILITY", "Liability"),
        ("INCOME", "Income"),
        ("EXPENSE", "Expense"),
        ("RESERVE", "Reserve"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="chart_of_accounts",
    )

    group = models.ForeignKey(
        "AccountGroup",
        on_delete=models.PROTECT,
        related_name="accounts",
        null=True,
        blank=True,
    )

    code = models.CharField(
        max_length=20,
        help_text="Short account code (e.g. MAINT, BANK, SINKFUND)",
    )

    name = models.CharField(
        max_length=255,
        help_text="Account name",
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
    )

    opening_balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
    )

    is_system = models.BooleanField(
        default=False,
        help_text="System-generated account (cannot be deleted)",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SocietyManager()

    class Meta:
        unique_together = ("society", "code")
        ordering = ["account_type", "code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def can_be_deleted(self):
        return not self.ledger_entries.exists()


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

    objects = SocietyManager()

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

    objects = SocietyManager()

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
    
    objects = SocietyManager()

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

    objects = SocietyManager()

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

    objects = SocietyManager()

    class Meta:
        ordering = ["-created_at"]
# society/models.py

class Vendor(models.Model):

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="vendors"
    )

    name = models.CharField(max_length=255)

    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    gst_number = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    bank_account_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bank_ifsc = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class VendorBill(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="vendor_bills"
    )

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="bills"
    )

    bill_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    bill_date = models.DateField()

    description = models.TextField(
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor} - ₹{self.amount}"

class VendorPayable(models.Model):

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("PARTIALLY_PAID", "Partially Paid"),
        ("PAID", "Paid"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="vendor_payables",
    )

    vendor_bill = models.OneToOneField(
        "VendorBill",
        on_delete=models.CASCADE,
        related_name="payable",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total amount of the bill",
    )

    outstanding_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Remaining unpaid amount",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor_bill.vendor} ₹{self.outstanding_amount}"

class VendorPayment(models.Model):

    PAYMENT_METHOD_CHOICES = [
        ("BANK_TRANSFER", "Bank Transfer"),
        ("UPI", "UPI"),
        ("CHEQUE", "Cheque"),
        ("CASH", "Cash"),
    ]

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="vendor_payments",
    )

    vendor_payable = models.ForeignKey(
        "VendorPayable",
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor_payable.vendor_bill.vendor} ₹{self.amount}"
           

from django.db import models
from django.core.exceptions import ValidationError

class AuditEvent(models.Model):
    event_type = models.CharField(max_length=128)
    actor_id = models.CharField(max_length=64, null=True, blank=True)

    domain = models.CharField(max_length=64)
    object_type = models.CharField(max_length=64)
    object_id = models.CharField(max_length=64)

    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    previous_hash = models.CharField(   # ✅ ADD THIS
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
    )

    event_hash = models.CharField(
        max_length=64,
        editable=False,
        db_index=True,
    )


    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit Event"
        verbose_name_plural = "Audit Events"

    def save(self, *args, **kwargs):
        # allow INSERT only
        if self.pk:
            raise ValidationError("Audit events are immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Audit events cannot be deleted.")

# Intelligence persistence models
from society.intelligence.persistence.models import IntelligenceMemoryEvent

class Person(models.Model):
    """
    Core human identity across the platform.
    One person can interact with multiple societies.
    Phone is the primary unique identifier.
    """

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person_profile",
        help_text="Linked authentication user account"
    )
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

class SocietyMember(models.Model):

    MEMBERSHIP_TYPES = [
        ("REGULAR", "Regular Member"),
        ("ASSOCIATE", "Associate Member"),
        ("NOMINAL", "Nominal Member"),
        ("PROVISIONAL", "Provisional Member"),
        ("INSTITUTIONAL", "Institutional Member"),
    ]

    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="members",
    )

    person = models.ForeignKey(
        "society.Person",
        on_delete=models.CASCADE,
        related_name="society_memberships",
    )

    membership_type = models.CharField(
        max_length=30,
        choices=MEMBERSHIP_TYPES,
    )

    member_number = models.CharField(max_length=50)

    admitted_on = models.DateField()

    ceased_on = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SocietyManager()

    class Meta:
        unique_together = ("society", "person")
        constraints = [
            models.UniqueConstraint(
                fields=["society", "member_number"],
                name="unique_member_number_per_society",
            )
        ]

    def __str__(self):
        return f"{self.person} ({self.member_number})"

class CommitteeMembership(models.Model):
    society = models.ForeignKey(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="committee_memberships",
    )

    member = models.ForeignKey(
        "society.SocietyMember",
        on_delete=models.CASCADE,
        related_name="committee_memberships",
    )

    elected_on = models.DateField()

    term_end = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = SocietyManager()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["society", "member"],
                condition=models.Q(is_active=True),
                name="unique_active_committee_member_per_society",
            )
        ]
        ordering = ["-elected_on"]

    def __str__(self):
        return f"{self.member} - Committee"

class Case(models.Model):
    """
    Represents a society formation / governance / legal case.
    First version focuses on pre-registration initiation.
    """

    CASE_TYPES = [
        ("prereg", "Pre-Registration"),
        ("handover", "Builder Handover"),
        ("legal", "Legal"),
    ]

    initiated_by = models.ForeignKey(Person, on_delete=models.CASCADE)
    case_type = models.CharField(max_length=20, choices=CASE_TYPES, default="prereg")
    
    society = models.OneToOneField(
        "society.Society",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="formation_case",
    )
    status = models.CharField(max_length=50, default="initiated")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_type} case by {self.initiated_by.full_name}"

class CaseStage(models.Model):
    """
    Represents each mandatory step in the society formation lifecycle.
    Auto-created when a Case is initiated.
    """

    STAGE_CODES = [
        ("member_list", "Member List"),
        ("share_structure", "Share Structure"),
        ("entrance_fees", "Entrance Fees"),
        ("promoter_affidavit", "Promoter Affidavit"),
        ("bank_account", "Bank Account"),
        ("building_docs", "Building Documents"),
        ("oc_cc", "OC / CC"),
        ("land_docs", "Land Documents"),
        ("builder_noc", "Builder NOC"),
        ("society_resolution", "Society Resolution"),
        ("bylaws_final", "Final By-laws"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="stages")

    stage_code = models.CharField(max_length=50, choices=STAGE_CODES)

    status = models.CharField(max_length=50, default="pending")
    document_generated = models.BooleanField(default=False)
    document_uploaded = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("case", "stage_code")

    def __str__(self):
        return f"{self.stage_code} — {self.case.id}"

# ==========================================================
# SOFT ONBOARDING TRACKER
# ==========================================================

class SoftOnboardingTracker(models.Model):
    """
    Tracks structural & finance readiness
    before legal preregistration completion.
    """

    society = models.OneToOneField(
        "society.Society",
        on_delete=models.CASCADE,
        related_name="soft_onboarding_tracker",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def evaluate_and_initialize(self):
        """
        If structure becomes ready and finance not yet initialized,
        trigger finance layer setup.
        """
        if not self.is_structure_ready():
            return

        if self.is_finance_ready():
            return

        # Lazy import to avoid circular dependency
        from statutory.onboarding.engine import StatutoryOnboardingEngine

        engine = StatutoryOnboardingEngine()
        engine._initialize_finance_layer(self.society)

    # -----------------------------
    # STRUCTURE CHECK
    # -----------------------------

    def is_structure_ready(self) -> bool:
        society = self.society

        if not society.wings.exists():
            return False

        if not society.flats.exists():
            return False

        if not society.members.exists():
            return False

        # Ensure floors exist via wing relation
        from society.models import Floor
        if not Floor.objects.filter(wing__society=society).exists():
            return False

        # Ensure all flats are properly linked
        unlinked_flats = society.flats.filter(
            models.Q(wing_ref__isnull=True) |
            models.Q(floor_ref__isnull=True)
        )

        if unlinked_flats.exists():
            return False

        return True

    # -----------------------------
    # FINANCE CHECK
    # -----------------------------

    def is_finance_ready(self) -> bool:
        return (
            self.society.chart_of_accounts.exists()
            and self.society.accounting_periods.exists()
        )

    # -----------------------------
    # OVERALL STATUS
    # -----------------------------

    def readiness_snapshot(self) -> dict:
        structure_ready = self.is_structure_ready()
        finance_ready = self.is_finance_ready()

        return {
            "structure_ready": structure_ready,
            "finance_ready": finance_ready,
            "overall_soft_ready": structure_ready and finance_ready,
        }

    def get_onboarding_stage(self) -> str:
        if not self.is_structure_ready():
            return "SOCIETY_SETUP"

        if self.is_structure_ready() and not self.is_finance_ready():
            return "STRUCTURE_DEFINED"

        if self.is_finance_ready():
            return "FINANCE_READY"

        return "SOCIETY_SETUP"


    def __str__(self):
        return f"SoftOnboardingTracker - {self.society.name}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Wing)
@receiver(post_save, sender=Floor)
@receiver(post_save, sender=Flat)
@receiver(post_save, sender=SocietyMember)
def evaluate_structure_on_change(sender, instance, **kwargs):
    society = getattr(instance, "society", None)

    # Floor gets society via wing
    if sender.__name__ == "Floor":
        society = instance.wing.society

    if not society:
        return

    try:
        tracker = society.soft_onboarding_tracker
        tracker.evaluate_and_initialize()
    except SoftOnboardingTracker.DoesNotExist:
        pass

class MaintenanceCharge(models.Model):

    society = models.ForeignKey(
        "Society",
        on_delete=models.CASCADE,
        related_name="maintenance_charges",
    )

    code = models.CharField(max_length=50)

    name = models.CharField(max_length=255)

    basis = models.CharField(
        max_length=50,
        choices=[
            ("EQUAL", "Equal Per Flat"),
            ("AREA", "Per Square Foot"),
            ("PER_SLOT", "Per Parking Slot"),
            ("PER_INLET", "Per Water Inlet"),
            ("PERCENT_MAINT", "% of Maintenance"),
        ],
    )

    rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    effective_from = models.DateField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

class MemberReceivable(models.Model):

    society = models.ForeignKey("Society", on_delete=models.CASCADE)

    flat = models.ForeignKey("Flat", on_delete=models.CASCADE)

    bill = models.ForeignKey(
        "FlatMaintenanceBill",
        on_delete=models.CASCADE,
        related_name="receivable"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=2)

    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("OPEN", "Open"),
            ("PARTIAL", "Partially Paid"),
            ("PAID", "Paid"),
        ],
        default="OPEN"
    )

    created_at = models.DateTimeField(auto_now_add=True)

class PaymentTransaction(models.Model):

    society = models.ForeignKey("Society", on_delete=models.CASCADE)

    flat = models.ForeignKey("Flat", on_delete=models.CASCADE)

    receivable = models.ForeignKey(
        "MemberReceivable",
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("UPI", "UPI"),
            ("BANK", "Bank Transfer"),
            ("CASH", "Cash"),
            ("CHEQUE", "Cheque"),
        ]
    )

    reference_number = models.CharField(max_length=100, blank=True)

    payment_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

class PaymentReceipt(models.Model):

    society = models.ForeignKey("Society", on_delete=models.CASCADE)

    payment = models.OneToOneField(
        "PaymentTransaction",
        on_delete=models.CASCADE,
        related_name="receipt"
    )

    receipt_number = models.CharField(max_length=50)

    issued_at = models.DateTimeField(auto_now_add=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

class NotificationEvent(models.Model):

    EVENT_TYPES = [
        ("MAINTENANCE_BILL", "Maintenance Bill Generated"),
        ("PAYMENT_RECEIPT", "Payment Receipt Generated"),
        ("NOTICE", "Legal Notice"),
    ]

    society = models.ForeignKey("Society", on_delete=models.CASCADE)

    flat = models.ForeignKey("Flat", on_delete=models.CASCADE)

    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)

    reference_id = models.CharField(max_length=100)

    payload = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default="PENDING"
    )
