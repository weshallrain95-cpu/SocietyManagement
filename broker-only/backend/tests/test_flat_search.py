"""Staff jump straight to a flat they have in mind: society (any spelling or nickname) + flat number."""

import pytest

from apps.inventory.search import parse_query
from apps.inventory.services import create_listing
from apps.masterdata import dedupe
from apps.masterdata.models import Building, Society, SocietyAlias, Unit
from common import rls

from .conftest import api_for

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "q,expected",
    [
        ("HE A-1203", ("HE", "1203", "A")),
        ("rodas a 1203", ("rodas", "1203", "A")),
        ("Lodha Amara 1501", ("Lodha Amara", "1501", "")),
        ("1203", ("", "1203", "")),
        ("B1203", ("", "1203", "B")),
        ("Hiranandani Estate", ("Hiranandani Estate", "", "")),
        ("Tower 7", ("Tower", "7", "")),
    ],
)
def test_parse_query(q, expected):
    assert parse_query(q) == expected


@pytest.fixture
def flats(society, thane, attrs, broker_a, broker_b):
    org, user = broker_a
    dedupe.learn_alias(society, "HE", SocietyAlias.Source.ADMIN)
    a = Building.objects.create(society=society, name="Rodas A", location=society.location)
    b = Building.objects.create(society=society, name="Rodas B", location=society.location)
    lodha = Society.objects.create(canonical_name="Lodha Amara", locality=thane["dhokali"], location=society.location)
    lb = Building.objects.create(society=lodha, name="Tower 3", location=society.location)
    out = {}
    with rls.org_context(org.pk):
        for bld, no in ((a, "1203"), (b, "1203"), (a, "1204"), (lb, "1203")):
            u = Unit.objects.create(building=bld, unit_no=no, bhk=2)
            out[f"{bld.name}/{no}"], _ = create_listing(org=org, user=user, unit=u, txn_type="RENT", data={"asking_rent": 20000})
    borg, buser = broker_b
    with rls.org_context(borg.pk):  # another broker's flat in the same building is never found
        u = Unit.objects.create(building=a, unit_no="1205", bhk=2)
        create_listing(org=borg, user=buser, unit=u, txn_type="RENT", data={"asking_rent": 20000})
    return org, user, out


def ids(r):
    return [(x["building"], x["unit_no"]) for x in r.json()["results"]]


def test_search_by_nickname_wing_and_flat(flats):
    org, user, _ = flats
    c = api_for(user, org)
    assert ids(c.get("/v1/listings/search", {"q": "HE A-1203"}))[0] == ("Rodas A", "1203")
    assert ids(c.get("/v1/listings/search", {"q": "hiranandni estate b 1203"}))[0] == ("Rodas B", "1203")
    assert ids(c.get("/v1/listings/search", {"q": "rodas a 1203"}))[0] == ("Rodas A", "1203")
    # flat number alone: every flat 1203 the broker has, across societies
    assert len(ids(c.get("/v1/listings/search", {"q": "1203"}))) == 3
    # society alone: all its flats, and the society is offered for adding a new flat
    r = c.get("/v1/listings/search", {"q": "Hiranandani Estate"}).json()
    assert len(r["results"]) == 3 and r["societies"][0]["name"] == "Hiranandani Estate"
    assert ids(c.get("/v1/listings/search", {"q": "HE 1205"})) == []  # other broker's flat stays private
    r = c.get("/v1/listings/search", {"q": "Lodha Amara 1203"}).json()
    assert [x["society"] for x in r["results"]] == ["Lodha Amara"]


def test_searched_flat_added_to_visit_plan(flats, as_org):
    org, user, out = flats
    c = api_for(user, org)
    cust = c.post("/v1/customers", {"phone": "9876543210", "name": "Riya", "source": "walk_in"}, format="json").json()
    hit = c.get("/v1/listings/search", {"q": "HE A-1204"}).json()["results"][0]
    plan = c.post(
        "/v1/visit-plans",
        {"customer_id": cust["id"], "listing_ids": [hit["id"]], "date": "2026-10-03", "start_time": "11:00"},
        format="json",
    ).json()
    other = c.get("/v1/listings/search", {"q": "lodha 1203"}).json()["results"][0]
    r = c.post(f"/v1/visit-plans/{plan['id']}/add-stop", {"listing_id": other["id"]}, format="json")
    assert r.status_code == 200 and [s["unit_no"] for s in r.json()["stops"]] == ["1204", "1203"]
