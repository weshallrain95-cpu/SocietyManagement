import datetime
import re

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point, Polygon
from rest_framework import serializers

from apps.identity.serializers import PhoneField
from apps.masterdata.models import Locality
from common import crypto

from .models import TXN_TYPES, BrokerOrg, Membership, ServiceArea


class LatLngField(serializers.Field):
    """{"lat": 19.2, "lng": 72.97} <-> Point."""

    def to_representation(self, value):
        return {"lat": value.y, "lng": value.x} if value else None

    def to_internal_value(self, data):
        try:
            lat, lng = float(data["lat"]), float(data["lng"])
        except (KeyError, TypeError, ValueError) as e:
            raise serializers.ValidationError('Expected {"lat": .., "lng": ..}') from e
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise serializers.ValidationError("Coordinates out of range")
        return Point(lng, lat, srid=4326)


class BrokerOrgSerializer(serializers.ModelSerializer):
    office_location = LatLngField(required=False, allow_null=True)
    txn_types = serializers.ListField(child=serializers.ChoiceField(choices=TXN_TYPES), min_length=1)

    class Meta:
        model = BrokerOrg
        fields = [
            "id",
            "name",
            "office_location",
            "office_address",
            "rera_agent_no",
            "txn_types",
            "languages",
            "verification_status",
            "rating_bayes",
            "rating_count",
            "median_response_s",
            "listing_accuracy",
            "closures",
            "plan_code",
        ]
        read_only_fields = [
            "verification_status",
            "rating_bayes",
            "rating_count",
            "median_response_s",
            "listing_accuracy",
            "closures",
            "plan_code",
        ]


class PublicBrokerSerializer(serializers.ModelSerializer):
    rera_registered = serializers.SerializerMethodField()

    class Meta:
        model = BrokerOrg
        fields = ["id", "name", "rera_registered", "rating_bayes", "rating_count", "median_response_s", "closures", "languages"]

    def get_rera_registered(self, org):
        return bool(org.rera_verified_at)


class StaffInviteSerializer(serializers.Serializer):
    phone = PhoneField()
    display_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[Membership.Role.MANAGER, Membership.Role.STAFF])


class MembershipSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Membership
        fields = ["id", "user_id", "name", "role", "permissions", "active", "created_at"]


class ServiceAreaSerializer(serializers.ModelSerializer):
    """Either a GeoJSON polygon, or a centre + radius (km) which we turn into a polygon."""

    geojson = serializers.JSONField(write_only=True, required=False)
    center = LatLngField(write_only=True, required=False)
    radius_km = serializers.FloatField(write_only=True, required=False, min_value=0.2, max_value=25)
    area_geojson = serializers.SerializerMethodField()

    class Meta:
        model = ServiceArea
        fields = ["id", "label", "locality", "txn_types", "geojson", "center", "radius_km", "area_geojson"]

    def get_area_geojson(self, obj):
        import json

        return json.loads(obj.area.geojson)

    def validate(self, attrs):
        if "geojson" in attrs:
            import json

            geom = GEOSGeometry(json.dumps(attrs.pop("geojson")), srid=4326)
        elif "center" in attrs and "radius_km" in attrs:
            geom = circle(attrs.pop("center"), attrs.pop("radius_km"))
        else:
            raise serializers.ValidationError("Give either geojson or center + radius_km")
        if isinstance(geom, Polygon):
            geom = MultiPolygon(geom, srid=4326)
        if not isinstance(geom, MultiPolygon) or not geom.valid:
            raise serializers.ValidationError("Service area must be a valid polygon")
        attrs["area"] = geom
        return attrs


def circle(center: Point, radius_km: float) -> Polygon:
    """Approximate circle via a metric projection (UTM 43N covers MMR)."""
    p = center.transform(32643, clone=True)
    poly = p.buffer(radius_km * 1000, quadsegs=16)
    poly.transform(4326)
    return poly


OWNER_ROLE = {
    "individual": "Owner",
    "proprietorship": "Proprietor",
    "partnership": "Partner",
    "llp": "Designated partner",
    "private_limited": "Director",
    "public_limited": "Director",
}
MIN_OWNERS = {"partnership": 2, "llp": 2}
LEGAL_FIELDS = ("legal_name", "ownership_type", "owners", "pan", "gstin", "gst_registered", "company_reg_no", "rera_agent_no")


class OwnerSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    role = serializers.CharField(max_length=40, required=False, allow_blank=True)

    def validate_name(self, v):
        v = " ".join(v.split())
        if len(v) < 3:
            raise serializers.ValidationError("Enter the full name")
        return v


class AgencyProfileSerializer(serializers.ModelSerializer):
    """First-time broker registration and the Admin's "Agency details" (founder decision 2026-09-25)."""

    txn_types = serializers.ListField(child=serializers.ChoiceField(choices=TXN_TYPES), min_length=1)
    owners = OwnerSerializer(many=True)
    pan = serializers.CharField(write_only=True, required=False, allow_blank=True)
    office_locality = serializers.PrimaryKeyRelatedField(queryset=Locality.objects.all(), required=False, allow_null=True)
    office_location = LatLngField(read_only=True)
    service_locality_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True, required=False)
    declaration = serializers.BooleanField(write_only=True, required=False)
    service_areas = serializers.SerializerMethodField()

    class Meta:
        model = BrokerOrg
        fields = [
            "id", "name", "legal_name", "ownership_type", "owners", "established_year",
            "pan", "pan_masked", "gst_registered", "gstin", "company_reg_no", "rera_agent_no",
            "contact_email", "office_address", "office_address_2", "office_locality", "office_city",
            "office_pincode", "office_state", "office_location", "txn_types", "languages",
            "service_locality_ids", "service_areas", "declaration", "declared_at",
            "verification_status", "verification_note",
        ]  # fmt: skip
        read_only_fields = ["pan_masked", "declared_at", "verification_status", "verification_note", "office_state"]

    def get_service_areas(self, org):
        return [] if org._state.adding else [{"id": str(a.pk), "label": a.label} for a in org.service_areas.all()]

    def validate(self, d):
        from .validators import RERA_AGENT_RE, clean_id, gstin_problem, pan_problem

        creating = self.instance is None
        cur = lambda k, default=None: d.get(k, getattr(self.instance, k, default) if self.instance else default)  # noqa: E731
        errors = {}
        required = ["name", "legal_name", "ownership_type", "owners", "office_address", "office_pincode", "office_locality"]
        for k in required:
            if creating and not d.get(k):
                errors[k] = "This is needed to register your agency"
        own = cur("ownership_type", "")
        if "owners" in d or "ownership_type" in d:
            owners = d.get("owners") if "owners" in d else list(self.instance.owners or [])
            need = MIN_OWNERS.get(own, 1)
            if own in ("individual", "proprietorship") and len(owners) != 1:
                errors["owners"] = "Give the one owner's full name"
            elif len(owners) < need:
                errors["owners"] = f"A {own.replace('_', ' ')} needs at least {need} names"
            d["owners"] = [{"name": o["name"], "role": OWNER_ROLE.get(own, "Owner")} for o in owners]
        if "pan" in d or creating:
            pan = clean_id(d.get("pan", ""))
            if not pan:
                errors["pan"] = "PAN is needed to register your agency"
            elif p := pan_problem(pan, own):
                errors["pan"] = p
            d["pan"] = pan
        pan_now = d.get("pan") or (crypto.decrypt(self.instance.pan_enc) if self.instance and self.instance.pan_enc else None)
        if "gst_registered" in d or "gstin" in d or creating:
            if cur("gst_registered", False):
                g = clean_id(d.get("gstin", cur("gstin", "")))
                if not g:
                    errors["gstin"] = "Enter the GSTIN, or untick 'Registered for GST'"
                elif p := gstin_problem(g, pan_now):
                    errors["gstin"] = p
                d["gstin"] = g
            else:
                d["gstin"] = ""
        if "rera_agent_no" in d:
            d["rera_agent_no"] = clean_id(d["rera_agent_no"])
        rera = cur("rera_agent_no", "")
        if rera and not RERA_AGENT_RE.match(rera):
            errors["rera_agent_no"] = "MahaRERA agent numbers look like A51700012345 (A and 11 digits)."
        if "SALE_NEW" in (cur("txn_types", []) or []) and not rera:
            errors["rera_agent_no"] = "A MahaRERA agent number is needed to sell new projects"
        if "office_pincode" in d and not re.fullmatch(r"[1-9]\d{5}", d["office_pincode"] or ""):
            errors["office_pincode"] = "Pincode should be 6 digits"
        y = d.get("established_year")
        if y is not None and not (1950 <= y <= datetime.date.today().year):
            errors["established_year"] = "Enter the year the business started"
        if creating:
            if not d.get("service_locality_ids"):
                errors["service_locality_ids"] = "Pick at least one area you serve"
            if d.get("declaration") is not True:
                errors["declaration"] = "Please confirm the declaration"
        if errors:
            raise serializers.ValidationError(errors)
        return d
