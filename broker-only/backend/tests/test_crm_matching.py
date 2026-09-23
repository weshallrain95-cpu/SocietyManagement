from datetime import timedelta

import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone

from apps.crm import services as crm
from apps.crm.models import Customer
from apps.inventory.services import create_listing
from apps.masterdata.location import compute_for_building
from apps.masterdata.models import Building, LocationFact, OwnershipClaim, Poi, Society, Unit
from apps.matching.engine import run
from apps.matching.services import match_requirement
from apps.status import services as st
from common import rls

from .conftest import DHOKALI, THANE_STN, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def pois(db):
    Poi.objects.create(type="rail_station", name="Thane", location=THANE_STN)
    Poi.objects.create(type="auto_stand", name="Dhokali Naka auto stand", location=Point(72.9785, 19.2265, srid=4326))
    Poi.objects.create(type="school", name="Vasant Vihar High School", location=Point(72.9760, 19.2285, srid=4326))


def _unit(society, no, bhk=2, bname="A"):
    b = Building.objects.filter(society=society, name=bname).first() or Building.objects.create(
        society=society, name=bname, location=society.location
    )
    return Unit.objects.create(building=b, unit_no=no, bhk=bhk)


@pytest.fixture
def inventory(society, attrs, pois, broker_a, broker_b):
    org, user = broker_a
    good = _unit(society, "1203")
    nopets = _unit(society, "1204")
    big = _unit(society, "1401", bhk=3)
    pricey = _unit(society, "1502")
    far_soc = Society.objects.create(
        canonical_name="Far Away Towers", locality=society.locality, location=Point(72.9300, 19.2700, srid=4326)
    )
    far = _unit(far_soc, "101")
    for b in Building.objects.all():
        compute_for_building(b)
    common = {"furnishing": "semi-furnished", "furn_gas_stove": "yes", "furn_kitchen_cabinet": "yes", "pets_allowed": "all pets"}
    with rls.org_context(org.pk):
        L = {}
        L["good"], _ = create_listing(org=org, user=user, unit=good, txn_type="RENT", data={"asking_rent": 24000}, attributes=common)
        L["nopets"], _ = create_listing(
            org=org, user=user, unit=nopets, txn_type="RENT", data={"asking_rent": 22000}, attributes={**common, "pets_allowed": "no"}
        )
        L["big"], _ = create_listing(
            org=org, user=user, unit=big, txn_type="RENT", data={"asking_rent": 25000, "bhk": 3}, attributes=common
        )
        L["pricey"], _ = create_listing(org=org, user=user, unit=pricey, txn_type="RENT", data={"asking_rent": 31000}, attributes=common)
        L["far"], _ = create_listing(org=org, user=user, unit=far, txn_type="RENT", data={"asking_rent": 20000}, attributes=common)
    # Broker B lists a perfect flat too; A must never see it.
    borg, buser = broker_b
    other = _unit(society, "1101")
    with rls.org_context(borg.pk):
        L["b_perfect"], _ = create_listing(
            org=borg, user=buser, unit=other, txn_type="RENT", data={"asking_rent": 21000}, attributes=common
        )
    return L


def test_riya_requirement(inventory, broker_a):
    """PRD persona: 2 BHK, ≤ ₹25k, around Dhokali, has a dog, needs gas stove + kitchen cabinet."""
    org, user = broker_a
    with rls.org_context(org.pk):
        riya, created = crm.capture_customer(org=org, user=user, phone="98765 43210", name="Riya", source="phone_call")
        assert created
        req = crm.add_requirement(
            riya,
            {
                "txn_type": "RENT",
                "bhk_min": 2,
                "bhk_max": 2,
                "budget_max": 25000,
                "search_area": _circle(DHOKALI, 2000),
                "must_haves": {"furn_gas_stove": True, "furn_kitchen_cabinet": True},
                "house_rule_needs": {"pets": "dog"},
            },
        )
        mr = match_requirement(req)
        results = {r.listing_id: r for r in mr.results.all()}
        ok = [lid for lid, r in results.items() if not r.excluded]
        assert ok == [inventory["good"].pk]
        assert results[inventory["nopets"].pk].excluded
        assert any(c["key"] == "pets_allowed" and c["result"] == "fail" for c in results[inventory["nopets"].pk].explanation)
        assert results[inventory["pricey"].pk].excluded
        assert results[inventory["far"].pk].excluded
        assert inventory["b_perfect"].pk not in results  # MATCH-01: never another broker's inventory
        good = results[inventory["good"].pk]
        assert {c["key"]: c["result"] for c in good.explanation}["furn_gas_stove"] == "ok"
        assert good.score > 50


def test_requirement_change_mid_tour_rematches(inventory, broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        c, _ = crm.capture_customer(org=org, user=user, phone="9876543211", source="walk_in")
        req = crm.add_requirement(c, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 3, "budget_max": 26000})
        before = {r.listing.pk for r in run(req, org_id=org.pk)}
        assert inventory["nopets"].pk in before and inventory["big"].pk in before
        crm.update_requirement(req, {"house_rule_needs": {"pets": "dog"}})
        after = {r.listing.pk for r in run(req, org_id=org.pk)}
        assert inventory["nopets"].pk not in after
        assert req.version == 2


def test_unknown_values_do_not_exclude(society, attrs, broker_a):
    org, user = broker_a
    u = _unit(society, "701")
    with rls.org_context(org.pk):
        create_listing(org=org, user=user, unit=u, txn_type="RENT", data={"asking_rent": 20000})
        c, _ = crm.capture_customer(org=org, user=user, phone="9876543212")
        req = crm.add_requirement(
            c,
            {
                "txn_type": "RENT",
                "bhk_min": 2,
                "bhk_max": 2,
                "budget_max": 25000,
                "must_haves": {"furn_gas_stove": True},
                "house_rule_needs": {"pets": "dog"},
            },
        )
        [r] = run(req, org_id=org.pk)
        chips = {c["key"]: c["result"] for c in r.explanation}
        assert chips["furn_gas_stove"] == "unknown" and chips["pets_allowed"] == "unknown"
        assert not r.excluded


def test_let_units_are_not_offered(inventory, broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        st.report(inventory["good"].unit, "RENT", "LET", st.Actor.broker(org))
        c, _ = crm.capture_customer(org=org, user=user, phone="9876543213")
        req = crm.add_requirement(c, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 25000})
        assert inventory["good"].pk not in {r.listing.pk for r in run(req, org_id=org.pk)}


def test_location_facts_are_computed(inventory):
    b = inventory["good"].unit.building
    f = LocationFact.objects.get(building=b, poi_type="rail_station")
    assert 4000 < f.distance_m < 5000  # Dhokali -> Thane station is ~4.6 km as the crow flies
    assert LocationFact.objects.get(building=b, poi_type="auto_stand").distance_m < 200


# --- offline customers -------------------------------------------------------


def test_offline_customer_capture_is_deduplicated(broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        a, c1 = crm.capture_customer(org=org, user=user, phone="+91 98765 00001", source="walk_in")
        b, c2 = crm.capture_customer(org=org, user=user, phone="09876500001", name="Imran", source="phone_call")
        assert a.pk == b.pk and c1 and not c2
        assert Customer.objects.get(pk=a.pk).name == "Imran"


def test_no_messages_without_consent(inventory, broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        c, _ = crm.capture_customer(org=org, user=user, phone="9876500002")
        sl = crm.create_shortlist(c, [inventory["good"]])
        with pytest.raises(crm.CrmError):
            crm.share_shortlist(sl, user=user)
        r = crm.request_consent(c, method="otp", user=user)
        crm.confirm_consent_otp(c, r["dev_code"], user=user)
        token = crm.share_shortlist(sl, user=user)
        item = sl.items.first()
    assert item is not None
    crm.respond_to_shortlist_item(token, item.pk, "interested")
    with rls.org_context(org.pk):
        item.refresh_from_db()
        assert item.customer_response == "interested"
        assert c.interactions.filter(kind="shortlist_response").exists()


def test_consent_via_link(broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        c, _ = crm.capture_customer(org=org, user=user, phone="9876500003")
        token = crm.request_consent(c, method="link", user=user)["token"]
    crm.confirm_consent_link(token, agree=True)
    with rls.org_context(org.pk):
        assert Customer.objects.get(pk=c.pk).consent_state == "link_confirmed"


def test_shortlist_cannot_include_other_brokers_listing(inventory, broker_a):
    org, user = broker_a
    with rls.org_context(org.pk):
        c, _ = crm.capture_customer(org=org, user=user, phone="9876500004")
        with pytest.raises(crm.CrmError):
            crm.create_shortlist(c, [inventory["b_perfect"]])


def test_offline_customer_claims_profile_on_signup(broker_a, broker_b):
    for org, user in (broker_a, broker_b):
        with rls.org_context(org.pk):
            crm.capture_customer(org=org, user=user, phone="9876500005")
    u = make_user("9876500005")
    assert crm.link_platform_user(u) == 2


def _circle(center, metres):
    from django.contrib.gis.geos import MultiPolygon

    p = center.transform(32643, clone=True).buffer(metres)
    p.transform(4326)
    return MultiPolygon(p, srid=4326)


def test_owner_verified_rule_beats_listing_broker(inventory, broker_a):
    """A verified owner saying 'no pets' removes the flat from dog-owner matches."""
    from apps.masterdata import resolver

    org, user = broker_a
    unit = inventory["good"].unit
    owner = make_user("9819000009")
    OwnershipClaim.objects.create(unit=unit, user=owner, status="verified", verified_at=timezone.now() - timedelta(days=1))
    resolver.record(unit, "pets_allowed", "no", source_type="owner_verified", user=owner)
    with rls.org_context(org.pk):
        c, _ = crm.capture_customer(org=org, user=user, phone="9876500006")
        req = crm.add_requirement(
            c, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 25000, "house_rule_needs": {"pets": "dog"}}
        )
        assert inventory["good"].pk not in {r.listing.pk for r in run(req, org_id=org.pk)}
