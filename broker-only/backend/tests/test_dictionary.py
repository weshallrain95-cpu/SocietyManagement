import pytest

from apps.masterdata import dictionary
from apps.masterdata.models import AttributeDef

pytestmark = pytest.mark.django_db


def test_approved_dictionary_loads_with_expected_tiers():
    rows, version = dictionary.rows_from_yaml(dictionary.DEFAULT_PATH)
    assert version == "1.0"
    dictionary.load_rows(rows, version)
    tiers = {t: AttributeDef.objects.filter(entry_tier=t).count() for t in ("essential", "recommended", "detailed", "system")}
    assert tiers == {"essential": 17, "recommended": 43, "detailed": 107, "system": 33}
    shared = AttributeDef.objects.filter(scope__in=["building", "society"]).count()
    assert shared == 91


def test_vocabulary_rule():
    """BRD 10.2: occupancy conditions are conduct-based; no identity terms anywhere in the dictionary."""
    text = dictionary.DEFAULT_PATH.read_text(encoding="utf-8").lower()
    for word in ("religio", "caste", "creed", "women", "men only", "gender", "community only"):
        assert word not in text
    rows, _ = dictionary.rows_from_yaml(dictionary.DEFAULT_PATH)
    assert next(r for r in rows if r["key"] == "bachelors_allowed")["allowed_values"] == ["allowed", "not allowed"]
