from datetime import timedelta

import pytest
from django.utils import timezone

from apps.masterdata import resolver
from apps.masterdata.models import ResolvedAttribute
from apps.masterdata.resolver import InvalidValue

pytestmark = pytest.mark.django_db


def _resolved(unit, key, subject_type="unit", subject_id=None):
    return ResolvedAttribute.objects.get(subject_type=subject_type, subject_id=subject_id or unit.pk, attr_id=key)


def test_owner_beats_brokers(unit, broker_a, broker_b):
    resolver.record(unit, "pets_allowed", "all pets", source_type="broker", org=broker_a[0])
    resolver.record(unit, "pets_allowed", "all pets", source_type="broker", org=broker_b[0])
    assert _resolved(unit, "pets_allowed").value == "all pets"
    resolver.record(unit, "pets_allowed", "no", source_type="owner_verified")
    ra = _resolved(unit, "pets_allowed")
    assert ra.value == "no" and ra.resolved_source_type == "owner_verified"


def test_fresh_report_outweighs_stale_one(unit, broker_a, broker_b):
    """Data Model §6.3 worked example."""
    resolver.record(unit, "pets_allowed", "no", source_type="broker", org=broker_b[0], observed_at=timezone.now() - timedelta(days=200))
    resolver.record(
        unit, "pets_allowed", "all pets", source_type="broker", org=broker_a[0], observed_at=timezone.now() - timedelta(days=10)
    )
    ra = _resolved(unit, "pets_allowed")
    assert ra.value == "all pets" and not ra.disputed


def test_genuine_disagreement_is_flagged(unit, broker_a, broker_b, db):
    from .conftest import make_org

    org_c = make_org("Third Broker", "9820000003")[0]
    resolver.record(unit, "furnishing", "semi-furnished", source_type="broker", org=broker_a[0])
    resolver.record(unit, "furnishing", "fully furnished", source_type="broker", org=broker_b[0])
    resolver.record(unit, "furnishing", "fully furnished", source_type="broker", org=org_c)
    ra = _resolved(unit, "furnishing")
    assert ra.value == "fully furnished"
    assert ra.support == 2
    # One dissenting actor is not a dispute; two would be.
    assert not ra.disputed


def test_a_broker_changing_their_mind_is_one_vote(unit, broker_a, broker_b):
    resolver.record(unit, "furnishing", "unfurnished", source_type="broker", org=broker_b[0])
    resolver.record(unit, "furnishing", "semi-furnished", source_type="broker", org=broker_a[0])
    resolver.record(unit, "furnishing", "unfurnished", source_type="broker", org=broker_a[0])
    ra = _resolved(unit, "furnishing")
    assert ra.value == "unfurnished" and ra.support == 2


def test_building_fact_reported_on_unit_lands_on_building(unit, broker_a):
    resolver.record(unit, "lift", "yes", source_type="broker", org=broker_a[0])
    assert _resolved(unit, "lift", "building", unit.building_id).value is True


def test_mirrors_to_unit_columns(unit, broker_a):
    resolver.record(unit, "bhk", "2.5", source_type="owner_verified")
    unit.refresh_from_db()
    assert float(unit.bhk) == 2.5


@pytest.mark.parametrize(
    "key,value,expected",
    [
        ("lift", "Yes", True),
        ("lift", "nahi", False),
        ("car_parking_covered", "1", 1),
        ("furnishing", "Semi furnished", "semi-furnished"),
        ("carpet_area_sqft", "1,050", 1050.0),
    ],
)
def test_value_validation(attrs, key, value, expected):
    from apps.masterdata.models import AttributeDef

    assert resolver.validate_value(AttributeDef.objects.get(key=key), value) == expected


def test_invalid_values_rejected(attrs):
    from apps.masterdata.models import AttributeDef

    with pytest.raises(InvalidValue):
        resolver.validate_value(AttributeDef.objects.get(key="pets_allowed"), "only goldfish")


def test_unknown_attribute_is_ignored(unit):
    assert resolver.record(unit, "helipad", True, source_type="broker") is None
