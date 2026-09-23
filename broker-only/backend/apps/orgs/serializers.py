from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point, Polygon
from rest_framework import serializers

from apps.identity.serializers import PhoneField

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
            "id", "name", "office_location", "office_address", "rera_agent_no", "txn_types", "languages",
            "verification_status", "rating_bayes", "rating_count", "median_response_s", "listing_accuracy",
            "closures", "plan_code",
        ]
        read_only_fields = [
            "verification_status", "rating_bayes", "rating_count", "median_response_s", "listing_accuracy",
            "closures", "plan_code",
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
        fields = ["id", "user_id", "name", "role", "active", "created_at"]


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
