"""Co-broking: a broker's trade network of fellow brokers (channel partners), founder decision D17.

- Every broker keeps their own list of fellow brokers (name, firm, number, office area). Like the
  customer list, it is the broker's private asset: no other firm ever sees it (RLS).
- A broker can blast flats from their own inventory, or a customer's requirement, to fellow brokers
  in and around the flat's location. The radius can be widened, or the broker sends to everyone on
  the list, or to names they tick.
- What goes out is trade-level only: society, area, BHK, rent/price, availability and the sending
  broker's name and number. Never the flat number, wing, owner, or the customer's identity, and no
  commission terms. It is a trade agreement between brokers: the owner is not asked.
- The platform never moves a flat into another broker's inventory. A fellow broker who has a customer
  replies; the sending broker stays in charge of the flat and the visit.
"""

from django.conf import settings
from django.contrib.gis.db import models as gis
from django.db import models

from common import crypto
from common.models import BaseModel


class FellowBroker(BaseModel):
    class Source(models.TextChoices):
        MANUAL = "manual"
        IMPORT = "import"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    name = models.CharField(max_length=120)
    firm = models.CharField(max_length=160, blank=True)
    phone_hash = models.CharField(max_length=64)
    phone_enc = models.BinaryField()
    address = models.CharField(max_length=300, blank=True)
    locality = models.ForeignKey("masterdata.Locality", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    location = gis.PointField(geography=True, null=True, blank=True, help_text="Office pin, if known")
    notes = models.CharField(max_length=300, blank=True)
    source = models.CharField(max_length=8, choices=Source.choices, default=Source.MANUAL)
    platform_org = models.ForeignKey(
        "orgs.BrokerOrg",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Their firm, if they use Only Broker",
    )
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["org", "phone_hash"], name="one_fellow_broker_per_phone_per_org")]

    @property
    def phone(self):
        return crypto.decrypt(self.phone_enc)


class TradeBlast(BaseModel):
    """What the sending firm sent, to whom (counts), and the replies it got. Private to the sender."""

    class Kind(models.TextChoices):
        FLATS = "flats"  # ready inventory from the broker's own list
        REQUIREMENT = "requirement"  # "does anyone have ...?" for one of the broker's customers

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    text = models.CharField(max_length=1000)
    items = models.JSONField(default=list, help_text="Trade-level summaries: never flat numbers, owners or customers")
    listing_ids = models.JSONField(default=list, blank=True)
    requirement = models.ForeignKey("crm.Requirement", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    audience = models.JSONField(default=dict, blank=True)
    recipients_total = models.PositiveIntegerField(default=0)
    delivered_in_app = models.PositiveIntegerField(default=0)
    via_whatsapp = models.PositiveIntegerField(default=0)


class TradeReply(BaseModel):
    """A fellow broker's answer to a blast, kept on the sender's side."""

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    blast = models.ForeignKey(TradeBlast, on_delete=models.CASCADE, related_name="replies")
    from_org = models.ForeignKey("orgs.BrokerOrg", null=True, on_delete=models.SET_NULL, related_name="+")
    from_name = models.CharField(max_length=160)
    from_phone_enc = models.BinaryField(null=True)
    message = models.CharField(max_length=300, blank=True)

    @property
    def from_phone(self):
        return crypto.decrypt(self.from_phone_enc) if self.from_phone_enc else ""


class TradeDelivery(BaseModel):
    """A blast as it landed in a fellow broker's trade inbox (their firm's row; a copy, not a link)."""

    class Reply(models.TextChoices):
        NONE = ""
        HAVE_CUSTOMER = "have_customer"  # answer to a flats blast
        HAVE_FLAT = "have_flat"  # answer to a requirement blast
        NOT_NOW = "not_now"

    org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+", db_column="broker_org_id")
    blast_id = models.UUIDField(db_index=True)
    from_org = models.ForeignKey("orgs.BrokerOrg", on_delete=models.CASCADE, related_name="+")
    from_name = models.CharField(max_length=160)
    from_phone_enc = models.BinaryField(null=True)
    kind = models.CharField(max_length=12, choices=TradeBlast.Kind.choices)
    text = models.CharField(max_length=1000)
    items = models.JSONField(default=list)
    read_at = models.DateTimeField(null=True, blank=True)
    reply = models.CharField(max_length=14, choices=Reply.choices, blank=True, default="")
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["org", "blast_id"], name="one_delivery_per_blast_per_org")]

    @property
    def from_phone(self):
        return crypto.decrypt(self.from_phone_enc) if self.from_phone_enc else ""
