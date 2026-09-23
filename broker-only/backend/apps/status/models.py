from django.conf import settings
from django.db import models

from common.models import BaseModel


class State(models.TextChoices):
    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    AVAILABLE_UNCONFIRMED = "AVAILABLE_UNCONFIRMED"
    ON_HOLD = "ON_HOLD"
    LET = "LET"
    SOLD = "SOLD"
    OFF_MARKET = "OFF_MARKET"


class TxnType(models.TextChoices):
    RENT = "RENT"
    SALE_NEW = "SALE_NEW"
    SALE_RESALE = "SALE_RESALE"


class UnitStatus(BaseModel):
    """Current master status of a unit for one transaction type (STAT-01)."""

    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="statuses")
    txn_type = models.CharField(max_length=12, choices=TxnType.choices)
    state = models.CharField(max_length=24, choices=State.choices, default=State.UNKNOWN)
    since = models.DateTimeField()
    last_confirmed_at = models.DateTimeField()
    source_type = models.CharField(max_length=20)
    confirmed_by_owner = models.BooleanField(default=False)
    available_from = models.DateField(null=True, blank=True)
    licence_end_date = models.DateField(null=True, blank=True)
    hold_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    version = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["unit", "txn_type"], name="uniq_unit_status")]
        indexes = [models.Index(fields=["state", "txn_type"])]

    @property
    def label(self) -> str:
        noun = "rent" if self.txn_type == TxnType.RENT else "sale"
        return {
            State.AVAILABLE: f"Available for {noun}",
            State.AVAILABLE_UNCONFIRMED: f"Available for {noun} – not yet confirmed by owner",
            State.ON_HOLD: "On hold (under negotiation)",
            State.LET: "Rented out",
            State.SOLD: "Sold",
            State.OFF_MARKET: "Off market",
            State.UNKNOWN: "Status unknown",
        }[self.state]


class StatusEvent(models.Model):
    """Append-only, hash-chained status ledger (STAT-07)."""

    seq = models.BigAutoField(primary_key=True)
    at = models.DateTimeField()
    unit_id = models.UUIDField(db_index=True)
    txn_type = models.CharField(max_length=12)
    from_state = models.CharField(max_length=24)
    to_state = models.CharField(max_length=24)
    actor_type = models.CharField(max_length=20)
    actor_org_id = models.UUIDField(null=True, blank=True)
    actor_user_id = models.UUIDField(null=True, blank=True)
    reason = models.CharField(max_length=300, blank=True)
    prev_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)

    def payload(self) -> dict:
        return {
            "at": self.at,
            "unit_id": self.unit_id,
            "txn_type": self.txn_type,
            "from": self.from_state,
            "to": self.to_state,
            "actor_type": self.actor_type,
            "actor_org_id": self.actor_org_id,
            "actor_user_id": self.actor_user_id,
            "reason": self.reason,
        }


class StatusReport(BaseModel):
    """Every availability claim, even ones that do not change state (needed for consensus, STAT-04)."""

    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="+")
    txn_type = models.CharField(max_length=12, choices=TxnType.choices)
    reported_state = models.CharField(max_length=24, choices=State.choices)
    actor_type = models.CharField(max_length=20)
    org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        indexes = [models.Index(fields=["unit", "txn_type", "reported_state", "created_at"])]


class StatusConfirmation(BaseModel):
    """A request to the verified owner to confirm availability (STAT-03/05)."""

    class Response(models.TextChoices):
        YES = "yes"
        NO = "no"
        AVAILABLE_FROM = "available_from"

    unit = models.ForeignKey("masterdata.Unit", on_delete=models.CASCADE, related_name="+")
    txn_type = models.CharField(max_length=12, choices=TxnType.choices)
    requested_state = models.CharField(max_length=24, choices=State.choices)
    previous_state = models.CharField(max_length=24, choices=State.choices)
    requested_by_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    link = models.OneToOneField("common.ShareLink", null=True, on_delete=models.SET_NULL, related_name="+")
    response = models.CharField(max_length=16, choices=Response.choices, blank=True)
    response_date = models.DateField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    channel = models.CharField(max_length=12, default="whatsapp")
