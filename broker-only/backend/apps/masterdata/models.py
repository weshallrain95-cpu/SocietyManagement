"""Master data: the shared, canonical registry of places and units (Data Model §3.2)."""
from django.conf import settings
from django.contrib.gis.db import models as gis
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models

from common.models import BaseModel

from .normalise import normalise_name, normalise_unit_no


class MicroMarket(BaseModel):
    class LaunchState(models.TextChoices):
        OFF = "off"
        PILOT = "pilot"
        LIVE = "live"

    name = models.CharField(max_length=80, unique=True)
    city = models.CharField(max_length=40, default="MMR")
    boundary = gis.MultiPolygonField(srid=4326, null=True, blank=True)
    launch_state = models.CharField(max_length=5, choices=LaunchState.choices, default=LaunchState.OFF)
    config = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name


class Locality(BaseModel):
    micro_market = models.ForeignKey(MicroMarket, on_delete=models.PROTECT, related_name="localities")
    name = models.CharField(max_length=80)
    name_normalised = models.CharField(max_length=80, db_index=True)
    pincodes = ArrayField(models.CharField(max_length=6), default=list, blank=True)
    centroid = gis.PointField(geography=True)
    boundary = gis.MultiPolygonField(srid=4326, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["micro_market", "name"], name="uniq_locality_name")]
        verbose_name_plural = "localities"

    def save(self, *a, **kw):
        self.name_normalised = normalise_name(self.name).text
        super().save(*a, **kw)

    def __str__(self):
        return self.name


class Society(BaseModel):
    class Kind(models.TextChoices):
        CHS = "chs"
        PROJECT = "project"
        STANDALONE = "standalone_building"
        LAYOUT = "layout"

    class Status(models.TextChoices):
        PROVISIONAL = "provisional"
        ACTIVE = "active"
        MERGED = "merged"
        REJECTED = "rejected"

    canonical_name = models.CharField(max_length=200)
    name_normalised = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.CHS)
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name="societies")
    address_line = models.CharField(max_length=300, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    location = gis.PointField(geography=True)
    boundary = gis.MultiPolygonField(srid=4326, null=True, blank=True)
    rera_project_nos = ArrayField(models.CharField(max_length=20), default=list, blank=True)
    possession_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    merged_into = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="+")
    proposed_by_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    provenance = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name_plural = "societies"
        indexes = [GinIndex(fields=["name_normalised"], name="society_name_trgm", opclasses=["gin_trgm_ops"])]

    def save(self, *a, **kw):
        self.name_normalised = normalise_name(self.canonical_name).text
        super().save(*a, **kw)

    def resolved(self) -> "Society":
        s = self
        while s.merged_into_id:
            s = s.merged_into
        return s

    def __str__(self):
        return self.canonical_name


class SocietyAlias(BaseModel):
    class Source(models.TextChoices):
        SEED = "seed"
        CANONICAL = "canonical"
        BROKER_UPLOAD = "broker_upload"
        BROKER_CONFIRMED = "broker_confirmed"
        ADMIN = "admin"
        MERGE = "merge"

    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="aliases")
    alias_raw = models.CharField(max_length=200)
    alias_normalised = models.CharField(max_length=200)
    source = models.CharField(max_length=20, choices=Source.choices)
    confirmations = models.PositiveIntegerField(default=1)
    created_by_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["alias_normalised", "society"], name="uniq_alias")]
        indexes = [GinIndex(fields=["alias_normalised"], name="alias_trgm", opclasses=["gin_trgm_ops"])]

    def save(self, *a, **kw):
        self.alias_normalised = normalise_name(self.alias_raw).text
        super().save(*a, **kw)


class Building(BaseModel):
    society = models.ForeignKey(Society, on_delete=models.PROTECT, related_name="buildings")
    name = models.CharField(max_length=80, help_text='"A Wing", "Tower 3"; "Main" when the society is one building')
    name_normalised = models.CharField(max_length=80)
    location = gis.PointField(geography=True)
    floors_total = models.PositiveSmallIntegerField(null=True, blank=True)
    lifts = models.PositiveSmallIntegerField(null=True, blank=True)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)
    merged_into = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["society", "name_normalised"], condition=models.Q(merged_into__isnull=True), name="uniq_building"
            )
        ]

    def save(self, *a, **kw):
        from .normalise import normalise_building

        self.name_normalised = normalise_building(self.name)
        super().save(*a, **kw)

    def __str__(self):
        return f"{self.society} – {self.name}"


class Unit(BaseModel):
    """One row per real, physical flat/house."""

    class PropertyType(models.TextChoices):
        APARTMENT = "apartment"
        ROW_HOUSE = "row_house"
        INDEPENDENT_HOUSE = "independent_house"
        VILLA = "villa"
        PENTHOUSE = "penthouse"
        STUDIO = "studio"

    building = models.ForeignKey(Building, on_delete=models.PROTECT, related_name="units")
    unit_no = models.CharField(max_length=30)
    unit_no_normalised = models.CharField(max_length=30)
    floor = models.SmallIntegerField(null=True, blank=True)
    location = gis.PointField(geography=True, null=True, blank=True, help_text="Defaults to building; override ≤ 150 m")
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.APARTMENT)
    bhk = models.DecimalField(max_digits=3, decimal_places=1, help_text="0.5 = 1RK")
    carpet_sqft = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    merged_into = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["building", "unit_no_normalised"], condition=models.Q(merged_into__isnull=True), name="uniq_unit"
            )
        ]

    def save(self, *a, **kw):
        self.unit_no_normalised = normalise_unit_no(self.unit_no).unit_no
        super().save(*a, **kw)

    @property
    def effective_location(self):
        return self.location or self.building.location

    def __str__(self):
        return f"{self.building} / {self.unit_no}"


class AttributeDef(models.Model):
    """The Unit Attribute Dictionary (founder-approved). Data, not code."""

    class ValueType(models.TextChoices):
        BOOL = "bool"
        ENUM = "enum"
        MULTI_ENUM = "multi_enum"
        INT = "int"
        NUMERIC = "numeric"
        MONEY = "money"
        DATE = "date"
        TEXT = "text"
        REF = "ref"

    class Authority(models.TextChoices):
        COMPUTED = "computed"
        OWNER = "owner"
        ANY = "any"
        ADMIN = "admin"

    class Scope(models.TextChoices):
        UNIT = "unit"
        BUILDING = "building"
        SOCIETY = "society"
        LISTING = "listing"

    class Matching(models.TextChoices):
        HARD = "hard"
        SOFT = "soft"
        DISPLAY = "display"

    key = models.SlugField(max_length=60, primary_key=True)
    label = models.CharField(max_length=120)
    label_i18n = models.JSONField(default=dict, blank=True)
    category = models.CharField(max_length=60)
    scope = models.CharField(max_length=10, choices=Scope.choices)
    value_type = models.CharField(max_length=12, choices=ValueType.choices)
    allowed_values = models.JSONField(default=list, blank=True)
    unit_label = models.CharField(max_length=40, blank=True)
    authority = models.CharField(max_length=10, choices=Authority.choices)
    matching = models.CharField(max_length=10, choices=Matching.choices)
    public = models.CharField(max_length=4, default="Y", help_text="Y, N or Band")
    applies_to = ArrayField(models.CharField(max_length=12), default=list)
    mvp = models.BooleanField(default=False)
    entry_tier = models.CharField(max_length=12, default="detailed", help_text="essential | recommended | detailed | system")
    asked_of = models.CharField(max_length=12, default="broker", help_text="broker | owner | building | nobody")
    display_order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    dictionary_version = models.CharField(max_length=20, default="")

    def __str__(self):
        return self.key


class AttributeObservation(BaseModel):
    """Every report of a value from any source. Append-only; the resolver reads these."""

    class Source(models.TextChoices):
        COMPUTED = "computed"
        OWNER_VERIFIED = "owner_verified"
        ADMIN = "admin"
        VISIT_FEEDBACK = "visit_feedback"
        BROKER = "broker"
        UPLOAD = "upload"
        CUSTOMER = "customer"
        OWNER_VIA_BROKER = "owner_via_broker"

    subject_type = models.CharField(max_length=10, choices=AttributeDef.Scope.choices)
    subject_id = models.UUIDField()
    attr = models.ForeignKey(AttributeDef, on_delete=models.PROTECT, db_column="attr_key")
    value = models.JSONField()
    source_type = models.CharField(max_length=20, choices=Source.choices)
    source_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    source_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    confidence = models.DecimalField(max_digits=3, decimal_places=2, default=1)
    observed_at = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["subject_type", "subject_id", "attr"])]


class ResolvedAttribute(models.Model):
    subject_type = models.CharField(max_length=10, choices=AttributeDef.Scope.choices)
    subject_id = models.UUIDField()
    attr = models.ForeignKey(AttributeDef, on_delete=models.PROTECT, db_column="attr_key")
    value = models.JSONField()
    resolved_source_type = models.CharField(max_length=20)
    support = models.PositiveIntegerField(default=1)
    disputed = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["subject_type", "subject_id", "attr"], name="uniq_resolved")]
        indexes = [models.Index(fields=["attr", "subject_type"])]


class Poi(BaseModel):
    class Type(models.TextChoices):
        RAIL_STATION = "rail_station"
        METRO_STATION = "metro_station"
        METRO_UPCOMING = "metro_upcoming"
        BUS_STOP = "bus_stop"
        AUTO_STAND = "auto_stand"
        SCHOOL = "school"
        HOSPITAL = "hospital"
        MARKET = "market"
        MALL = "mall"
        PARK = "park"
        HIGHWAY = "highway"
        ATM_BANK = "atm_bank"
        PHARMACY = "pharmacy"
        POLICE_STATION = "police_station"

    type = models.CharField(max_length=20, choices=Type.choices, db_index=True)
    name = models.CharField(max_length=160)
    location = gis.PointField(geography=True)
    source = models.CharField(max_length=20, default="osm")
    verified = models.BooleanField(default=False)


class LocationFact(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="location_facts")
    poi_type = models.CharField(max_length=20, choices=Poi.Type.choices)
    poi = models.ForeignKey(Poi, on_delete=models.CASCADE)
    poi_name = models.CharField(max_length=160)
    distance_m = models.PositiveIntegerField()
    walk_min = models.PositiveSmallIntegerField()
    drive_min = models.PositiveSmallIntegerField()
    method = models.CharField(max_length=12, default="estimate", help_text="estimate | routes_api")
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["building", "poi_type"], name="uniq_fact")]


class OwnershipClaim(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        VERIFIED = "verified"
        REJECTED = "rejected"
        REVOKED = "revoked"

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="ownership_claims")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ownership_claims")
    proof_type = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    attested_by_org = models.ForeignKey("orgs.BrokerOrg", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    verified_at = models.DateTimeField(null=True, blank=True)
