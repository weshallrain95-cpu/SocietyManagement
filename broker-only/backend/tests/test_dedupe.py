import pytest
from django.contrib.gis.geos import Point

from apps.masterdata import dedupe
from apps.masterdata.models import Building, Society, SocietyAlias, Unit
from apps.masterdata.services import get_or_create_building, merge_societies
from common import rls

from .conftest import DHOKALI, MANPADA

pytestmark = pytest.mark.django_db


@pytest.fixture
def registry(thane):
    dh, mp = thane["dhokali"], thane["manpada"]
    mk = lambda name, loc, pt, pin: Society.objects.create(canonical_name=name, locality=loc, location=pt, pincode=pin)  # noqa: E731
    return {
        "he": mk("Hiranandani Estate", dh, DHOKALI, "400607"),
        "vasant": mk("Vasant Vihar", mp, MANPADA, "400610"),
        "lodha": mk("Lodha Amara", dh, Point(72.9810, 19.2250, srid=4326), "400607"),
        "shanti_dh": mk("Shanti Niwas", dh, Point(72.9790, 19.2290, srid=4326), "400607"),
        "shanti_mp": mk("Shanti Niwas", mp, Point(72.9690, 19.2340, srid=4326), "400610"),
    }


@pytest.mark.parametrize("raw", ["Hiranandani Estate", "HIRANANDANI ESTATE CHS LTD", "Hira Nandani Est.", "hiranandani estate, thane"])
def test_spelling_variants_auto_match(registry, thane, raw):
    d = dedupe.decide(dedupe.find_candidates(raw, micro_market=thane["mm"]))
    assert d.action == "auto", [c.as_dict() for c in d.candidates]
    assert d.best.society == registry["he"]


def test_same_name_in_two_localities_needs_a_human(registry, thane):
    d = dedupe.decide(dedupe.find_candidates("Shanti Niwas", micro_market=thane["mm"]))
    assert d.action == "confirm"
    assert {c.society for c in d.candidates[:2]} == {registry["shanti_dh"], registry["shanti_mp"]}


def test_locality_breaks_the_tie(registry, thane):
    d = dedupe.decide(dedupe.find_candidates("Shanti Niwas", locality=thane["manpada"], micro_market=thane["mm"]))
    assert d.action == "auto"
    assert d.best.society == registry["shanti_mp"]


def test_unknown_name_becomes_provisional(registry, thane):
    d = dedupe.decide(dedupe.find_candidates("Kalpataru Srishti", micro_market=thane["mm"]))
    assert d.action == "provisional"


def test_geo_cannot_rescue_a_different_name(registry, thane):
    cands = dedupe.find_candidates("Sai Darshan", point=DHOKALI, micro_market=thane["mm"])
    assert dedupe.decide(cands).action == "provisional"


def test_short_form_learned_as_alias_then_auto_matches(registry, thane):
    first = dedupe.decide(dedupe.find_candidates("HE Rodas", micro_market=thane["mm"]))
    assert first.action != "auto"
    dedupe.learn_alias(registry["he"], "HE Rodas", SocietyAlias.Source.BROKER_CONFIRMED)
    again = dedupe.decide(dedupe.find_candidates("HE Rodas", micro_market=thane["mm"]))
    assert again.action == "auto" and again.best.society == registry["he"]


def test_merge_repoints_buildings_units_and_listings(registry, thane, attrs, broker_a):
    from django.utils import timezone

    from apps.inventory.models import Listing

    dup = Society.objects.create(canonical_name="Hira Nandani Estate", locality=thane["dhokali"], location=DHOKALI,
                                 status=Society.Status.PROVISIONAL)
    b_real = get_or_create_building(registry["he"], "Rodas A")
    b_dup = get_or_create_building(dup, "A Rodas") if False else get_or_create_building(dup, "Rodas A")
    u_real = Unit.objects.create(building=b_real, unit_no="1203", bhk=2)
    u_dup = Unit.objects.create(building=b_dup, unit_no="B-1203", bhk=2)
    Unit.objects.create(building=b_dup, unit_no="1204", bhk=2)
    org = broker_a[0]
    with rls.org_context(org.pk):
        Listing.objects.create(org=org, unit=u_dup, txn_type="RENT", last_confirmed_at=timezone.now())
    with rls.platform_context():
        result = merge_societies(dup, registry["he"], user=None)
    assert result["merged_units"] == 1
    dup.refresh_from_db()
    assert dup.status == "merged" and dup.merged_into == registry["he"]
    assert Unit.objects.get(pk=u_dup.pk).merged_into == u_real
    assert Building.objects.get(pk=b_dup.pk).merged_into == b_real
    with rls.org_context(org.pk):
        assert Listing.objects.get().unit == u_real
    assert SocietyAlias.objects.filter(society=registry["he"], alias_normalised="hira nandani estate").exists()
