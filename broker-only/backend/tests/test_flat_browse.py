"""Approved design (2026-09-24): a broker with 1,000 flats finds any one from a single search box — society,
wing, flat number, owner name or owner phone — with filters, quick views and browse-by-society; and the flat
page carries facts, house rules, distances, fitting customers, activity and the private block."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.crm import services as crm
from apps.inventory.models import Listing
from apps.inventory.services import create_listing, set_keys
from apps.masterdata.models import Building, Unit
from apps.orgs.models import Membership
from common import rls

from .conftest import api_for, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def book(society, thane, attrs, broker_a, broker_b):
    org, user = broker_a
    borg, buser = broker_b
    a = Building.objects.create(society=society, name="Rodas A", location=society.location, floors_total=20)
    b = Building.objects.create(society=society, name="Rodas B", location=society.location, floors_total=20)
    u1 = Unit.objects.create(building=a, unit_no="1203", floor=12, bhk=2, carpet_sqft=650)
    u2 = Unit.objects.create(building=a, unit_no="504", floor=5, bhk=1)
    u3 = Unit.objects.create(building=b, unit_no="1202", floor=12, bhk=3)
    with rls.org_context(org.pk):
        l1, _ = create_listing(
            org=org,
            user=user,
            unit=u1,
            txn_type="RENT",
            data={"asking_rent": 24000, "owner_name": "Mrs Kulkarni"},
            owner_phone="9819012345",
            attributes={"pets_allowed": "all pets", "furnishing": "semi-furnished", "furn_gas_stove": True},
        )
        l2, _ = create_listing(org=org, user=user, unit=u2, txn_type="RENT", data={"asking_rent": 16000, "owner_name": "Mr Shah"})
        l3, _ = create_listing(org=org, user=user, unit=u3, txn_type="RENT", data={"asking_rent": 38000, "owner_name": "Mr Desai"})
        set_keys(l1, holder_type="office", instructions="drawer 3")
        Listing.objects.filter(pk=l3.pk).update(last_confirmed_at=timezone.now() - timedelta(days=30))
        riya, _ = crm.capture_customer(org=org, user=user, phone="9876543210", name="Riya", source="walk_in")
        crm.add_requirement(riya, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 25000}, localities=[thane["dhokali"]])
        low, _ = crm.capture_customer(org=org, user=user, phone="9876500001", name="Low budget", source="walk_in")
        crm.add_requirement(low, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 15000})
    with rls.org_context(borg.pk):
        create_listing(org=borg, user=buser, unit=u1, txn_type="RENT", data={"asking_rent": 25000, "owner_name": "Kulkarni"})
    return {"api": api_for(user, org), "org": org, "l1": l1, "l2": l2, "l3": l3, "a": a}


def ids(r):
    return [x["unit_no"] for x in r["results"]]


def test_one_box_finds_any_flat(book):
    c = book["api"]
    assert ids(c.get("/v1/listings/browse", {"q": "hiranandani a-1203"}).json()) == ["1203"]
    assert sorted(ids(c.get("/v1/listings/browse", {"q": "rodas 12"}).json())) == ["1202", "1203"]
    assert ids(c.get("/v1/listings/browse", {"q": "kulkarni"}).json()) == ["1203"]  # owner name
    assert ids(c.get("/v1/listings/browse", {"q": "98190 12345"}).json()) == ["1203"]  # owner phone
    assert ids(c.get("/v1/listings/browse", {"q": "+91 98190 99999"}).json()) == []
    r = c.get("/v1/listings/browse").json()
    assert r["count"] == 3  # never broker B's listing of the same flat
    assert r["counts"] == {"total": 3, "available_now": 3, "reconfirm": 1, "new": 3, "keys_office": 1, "no_photos": 3}


def test_broker_builds_available_now_from_all_flats(book):
    c, l1, l2, l3 = book["api"], book["l1"], book["l2"], book["l3"]
    with rls.org_context(book["org"].pk):  # e.g. uploaded as the whole inventory
        Listing.objects.update(available_now=False)
    r = c.get("/v1/listings/browse", {"list": "available_now"}).json()
    assert r["count"] == 0 and r["counts"]["total"] == 3 and r["counts"]["available_now"] == 0
    assert r["counts"]["reconfirm"] == 0  # nothing on offer, so nothing to reconfirm

    # Pick two flats from all flats; one was rented out, so it comes back as available (unconfirmed).
    c.post(f"/v1/listings/{l2.pk}/status", {"state": "LET"}, format="json")
    r = c.post("/v1/listings/available-now", {"listing_ids": [str(l1.pk), str(l2.pk)], "available_now": True}, format="json")
    assert r.json() == {"changed": 2, "available_now": True}
    assert sorted(ids(c.get("/v1/listings/browse", {"list": "available_now"}).json())) == sorted([l1.unit.unit_no, l2.unit.unit_no])
    assert c.get(f"/v1/listings/{l2.pk}").json()["status"] == "AVAILABLE_UNCONFIRMED"

    # On hold stays in the list (the deal can fall through); rented out leaves it and stays in all flats.
    c.post(f"/v1/listings/{l1.pk}/status", {"state": "ON_HOLD"}, format="json")
    c.post(f"/v1/listings/{l2.pk}/status", {"state": "LET"}, format="json")
    assert ids(c.get("/v1/listings/browse", {"list": "available_now"}).json()) == [l1.unit.unit_no]
    assert c.get("/v1/listings/browse").json()["count"] == 3
    assert c.get(f"/v1/listings/{l2.pk}").json()["available_now"] is False

    # Taking a flat off the list; a new flat added by hand is available now unless the broker says no.
    c.post("/v1/listings/available-now", {"listing_ids": [str(l1.pk)], "available_now": False}, format="json")
    assert c.get("/v1/listings/browse", {"list": "available_now"}).json()["count"] == 0
    assert l3.unit.unit_no not in ids(c.get("/v1/listings/browse", {"list": "available_now"}).json())


def test_filters_sort_and_paging(book):
    c = book["api"]
    assert ids(c.get("/v1/listings/browse", {"bhk": "2,3", "sort": "price_low"}).json()) == ["1203", "1202"]
    assert ids(c.get("/v1/listings/browse", {"price_max": "20000"}).json()) == ["504"]
    assert ids(c.get("/v1/listings/browse", {"quick": "keys_office"}).json()) == ["1203"]
    assert ids(c.get("/v1/listings/browse", {"quick": "reconfirm"}).json()) == ["1202"]
    assert ids(c.get("/v1/listings/browse", {"building_id": str(book["a"].pk), "sort": "price_high"}).json()) == ["1203", "504"]
    page = c.get("/v1/listings/browse", {"sort": "price_high", "limit": 2, "offset": 2}).json()
    assert page["count"] == 3 and ids(page) == ["504"]
    first = c.get("/v1/listings/browse", {"q": "1203"}).json()["results"][0]
    assert (first["owner_name"], first["keys_holder"], first["photo_count"], first["carpet_sqft"]) == ("Mrs Kulkarni", "office", 0, 650.0)
    tree = c.get("/v1/listings/by-society").json()
    assert tree[0]["name"] == "Hiranandani Estate" and tree[0]["count"] == 3
    assert [(w["name"], w["count"]) for w in tree[0]["wings"]] == [("Rodas A", 2), ("Rodas B", 1)]


def test_flat_page_sections(book):
    p = book["api"].get(f"/v1/listings/{book['l1'].pk}").json()["page"]
    facts = {f["label"]: f["value"] for f in p["facts"]}
    assert facts["Floor"] == "12 of 20" and facts["Carpet area"] == "650 sq ft" and facts["Furnishing"] == "Semi-furnished"
    assert {"label": "Pets allowed", "value": "All pets", "tone": "ok"} in p["house_rules"]
    assert "Gas stove" in p["in_flat"]
    assert p["fitting_customers"]["count"] == 1 and p["fitting_customers"]["customers"][0]["name"] == "Riya"
    assert p["other_brokers"] == 1  # a number, never who
    assert "Kulkarni" not in str(p["activity"]) and p["activity"][-1]["text"].startswith("Added to your flats")
    assert p["building"]["floors_total"] == 20 and p["locality"] == "Dhokali"


def test_field_staff_see_only_assigned_and_no_private_sections(book):
    staff_user = make_user("9820011111", "Imran")
    Membership.objects.create(user=staff_user, org=book["org"], role=Membership.Role.STAFF)
    staff = api_for(staff_user, book["org"], role="broker_staff")
    assert staff.get("/v1/listings/browse").json()["count"] == 0
    assert staff.get("/v1/listings/by-society").json() == []
