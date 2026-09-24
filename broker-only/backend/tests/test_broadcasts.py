"""D16: brokers broadcast news to their own customers (the broker's second asset), delivered in the app.

Pilot rules: all of the firm's customers (a customer can turn a broker's updates off); free; customers
not on the app are listed with a WhatsApp invite. Never another firm's customers; never a flat number.
"""

import pytest

from apps.crm import services as crm
from apps.crm.models import Broadcast
from apps.inventory.services import create_listing
from apps.masterdata.models import Building, Unit
from apps.orgs.models import Membership
from common import rls

from .conftest import api_for, make_user
from .test_api_journeys import login

pytestmark = pytest.mark.django_db


@pytest.fixture
def book(society, thane, attrs, broker_a, broker_b):
    """Broker A: Riya (on the app), Karan (offline), Meera (on the app, looking in Manpada). Broker B: Riya too."""
    org, user = broker_a
    borg, buser = broker_b
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    u = Unit.objects.create(building=b, unit_no="1203", bhk=2)
    with rls.org_context(org.pk):
        listing, _ = create_listing(org=org, user=user, unit=u, txn_type="RENT", data={"asking_rent": 24000})
        riya, _ = crm.capture_customer(org=org, user=user, phone="9876543210", name="Riya", source="walk_in")
        crm.capture_customer(org=org, user=user, phone="9876500001", name="Karan", source="phone_call")
        meera, _ = crm.capture_customer(org=org, user=user, phone="9876500002", name="Meera", source="walk_in")
        crm.add_requirement(meera, {"txn_type": "RENT", "bhk_min": 1, "bhk_max": 2, "budget_max": 30000}, localities=[thane["manpada"]])
    with rls.org_context(borg.pk):
        crm.capture_customer(org=borg, user=buser, phone="9876543210", name="Riya", source="walk_in")
    riya_app, _ = login("9876543210")  # logging in links Riya's records with both brokers
    meera_app, _ = login("9876500002")
    return {"api": api_for(user, org), "org": org, "borg": borg, "listing": listing, "riya": riya_app, "meera": meera_app}


def test_preview_suggests_text_and_counts_reach(book):
    c = book["api"]
    r = c.get("/v1/broadcasts/preview", {"kind": "new_flat", "listing_id": str(book["listing"].pk)}).json()
    assert r["text"].startswith("New 2 BHK for rent in Hiranandani Estate, Dhokali — ₹24,000/month")
    assert "1203" not in r["text"]  # never the flat number
    assert r["reach"] == {"total": 3, "in_app": 2, "muted": 0, "not_on_app": 1} and r["free_in_pilot"]


def test_send_reaches_own_customers_in_app_and_lists_offline_ones(book):
    c = book["api"]
    r = c.post("/v1/broadcasts", {"kind": "new_flat", "listing_id": str(book["listing"].pk)}, format="json")
    assert r.status_code == 201, r.content
    body = r.json()
    assert (body["delivered_in_app"], body["not_on_app"]) == (2, 1)
    assert body["invite"][0]["name"] == "Karan" and body["invite"][0]["whatsapp_url"].startswith("https://wa.me/919876500001?text=")
    upd = book["riya"].get("/v1/me/updates").json()
    assert len(upd) == 1 and upd[0]["org"] == "Suresh Realty" and upd[0]["flat"]["society"] == "Hiranandani Estate"
    assert "1203" not in str(upd[0])
    with rls.org_context(book["borg"].pk):
        assert Broadcast.objects.count() == 0  # the log is private to the sending firm


def test_area_audience_and_mute(book, thane):
    c = book["api"]
    r = c.post("/v1/broadcasts", {"kind": "price_drop", "locality_id": str(thane["manpada"].pk), "scope": "locality"}, format="json").json()
    assert (r["recipients_total"], r["delivered_in_app"]) == (1, 1) and "Manpada" in r["text"]
    assert book["riya"].get("/v1/me/updates").json() == []  # not looking in Manpada

    org_id = str(book["org"].pk)
    assert book["riya"].post("/v1/me/updates/mute", {"org_id": org_id, "muted": True}, format="json").json()["updated"] == 1
    r = c.post("/v1/broadcasts", {"kind": "news", "text": "Office closed on Sunday"}, format="json").json()
    assert (r["delivered_in_app"], r["muted"]) == (1, 1)
    assert book["riya"].get("/v1/me/updates").json() == []
    book["riya"].post("/v1/me/updates/mute", {"org_id": org_id, "muted": False}, format="json")
    assert c.post("/v1/broadcasts", {"kind": "news", "text": "Diwali offer"}, format="json").json()["delivered_in_app"] == 2


def test_rules(book, broker_b):
    c = book["api"]
    assert c.post("/v1/broadcasts", {"kind": "news", "text": ""}, format="json").status_code == 400
    assert c.post("/v1/broadcasts", {"kind": "news", "text": "x" * 501}, format="json").status_code == 400
    borg, buser = broker_b
    other = api_for(buser, borg)
    r = other.post("/v1/broadcasts", {"kind": "new_flat", "listing_id": str(book["listing"].pk)}, format="json")
    assert r.status_code == 404  # another firm's flat is invisible
    staff_user = make_user("9820011111", "Imran")
    Membership.objects.create(user=staff_user, org=book["org"], role=Membership.Role.STAFF)
    staff = api_for(staff_user, book["org"], role="broker_staff")
    assert staff.post("/v1/broadcasts", {"kind": "news", "text": "hi"}, format="json").status_code == 403  # field staff can't broadcast
