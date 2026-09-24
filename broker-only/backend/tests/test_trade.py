"""D17: co-broking. A broker blasts ready flats (or a customer's requirement) to fellow brokers from their
own trade list, in and around the flat, widened or hand-picked. Trade-level details only: never the flat
number, wing, owner or customer, no commission terms, and no flat ever moves into another broker's inventory.
"""

import pytest

from apps.crm import services as crm
from apps.inventory.models import Listing
from apps.inventory.services import create_listing
from apps.masterdata.models import Building, Unit
from apps.orgs.models import Membership
from apps.trade.models import FellowBroker, TradeBlast, TradeDelivery
from common import rls
from common.models import Notification

from .conftest import api_for, make_user

pytestmark = pytest.mark.django_db

CSV = b"""Broker Name,Agency,Mobile,Area
Om Sai,Om Sai Estate Agents,9820000002,Manpada
Ramesh Patil,Patil Properties,98203 00001,"Shop 4, Manpada Road"
Anil,,9820300003,
Bad row,,12345,Dhokali
"""


@pytest.fixture
def net(society, thane, attrs, broker_a, broker_b):
    org, user = broker_a
    borg, buser = broker_b
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    u = Unit.objects.create(building=b, unit_no="1203", bhk=2)
    with rls.org_context(org.pk):
        listing, _ = create_listing(
            org=org,
            user=user,
            unit=u,
            txn_type="RENT",
            data={"asking_rent": 24000, "owner_name": "Mr Kulkarni", "brokerage_terms": "50-50"},
        )
        cust, _ = crm.capture_customer(org=org, user=user, phone="9876500009", name="Priya Shah", source="walk_in")
        req = crm.add_requirement(
            cust, {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 30000}, localities=[thane["manpada"]]
        )
    a = api_for(user, org)
    r = a.post("/v1/trade/contacts/import", {"file": _file("brokers.csv", CSV)}, format="multipart")
    assert r.status_code == 200, r.content
    assert (r.json()["added"], r.json()["skipped_count"]) == (3, 1)
    # Vikram's office pin is near Thane station, ~4.6 km from the flat.
    r = a.post("/v1/trade/contacts", {"name": "Vikram", "phone": "9820300002", "lat": 19.1860, "lng": 72.9750}, format="json")
    assert r.status_code == 201
    return {"a": a, "b": api_for(buser, borg), "org": org, "borg": borg, "listing": listing, "req": req}


def _file(name, content):
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(name, content)


def _ids(rows, names):
    return [r["id"] for r in rows if r["name"] in names]


def test_the_list_knows_who_is_on_the_platform_and_where(net):
    rows = {r["name"]: r for r in net["a"].get("/v1/trade/contacts").json()}
    assert rows["Om Sai"]["on_platform"] and rows["Om Sai"]["locality"] == "Manpada"
    assert rows["Ramesh Patil"]["locality"] == "Manpada" and not rows["Ramesh Patil"]["on_platform"]
    assert not rows["Anil"]["has_location"]
    assert net["a"].get("/v1/trade/contacts", {"q": "patil"}).json()[0]["name"] == "Ramesh Patil"
    with rls.org_context(net["borg"].pk):
        assert FellowBroker.objects.count() == 0  # a broker's trade list is theirs alone


def test_preview_in_and_around_the_flat_then_wider_then_everyone(net):
    q = {"kind": "flats", "listing_ids": str(net["listing"].pk)}
    p = net["a"].get("/v1/trade/blasts/preview", q).json()
    assert [c["name"] for c in p["contacts"] if c["selected"]] == ["Om Sai", "Ramesh Patil"]
    assert p["reach"] == {"total": 4, "selected": 2, "in_app": 1, "whatsapp": 1, "no_location": 1}
    assert p["text"].startswith("Ready flat available:\n• 2 BHK for rent, Hiranandani Estate, Dhokali — ₹24,000/month")
    for secret in ("1203", "Rodas", "Kulkarni", "50-50"):
        assert secret not in str(p["items"]) + p["text"]
    wider = net["a"].get("/v1/trade/blasts/preview", q | {"radius_km": 6}).json()
    assert [c["name"] for c in wider["contacts"] if c["selected"]] == ["Om Sai", "Ramesh Patil", "Vikram"]
    assert net["a"].get("/v1/trade/blasts/preview", q | {"scope": "all"}).json()["reach"]["selected"] == 4
    anil = _ids(p["contacts"], {"Anil"})
    picked = net["a"].get("/v1/trade/blasts/preview", q | {"scope": "selected", "contact_ids": ",".join(anil)}).json()
    assert [c["name"] for c in picked["contacts"] if c["selected"]] == ["Anil"]


def test_send_lands_in_fellow_inbox_and_replies_come_back(net):
    before_b = _listing_count(net["borg"])
    r = net["a"].post("/v1/trade/blasts", {"kind": "flats", "listing_ids": [str(net["listing"].pk)]}, format="json")
    assert r.status_code == 201, r.content
    body = r.json()
    assert (body["recipients_total"], body["delivered_in_app"], body["via_whatsapp"]) == (2, 1, 1)
    assert body["whatsapp"][0]["name"] == "Ramesh Patil" and body["whatsapp"][0]["whatsapp_url"].startswith(
        "https://wa.me/919820300001?text="
    )

    inbox = net["b"].get("/v1/trade/inbox").json()
    assert len(inbox) == 1 and inbox[0]["from"] == "Suresh Realty" and inbox[0]["from_phone"] == "+919820000001"
    assert "1203" not in str(inbox[0]["items"]) + inbox[0]["text"]
    assert Notification.objects.filter(org_id=net["borg"].pk, template="trade_blast").exists()
    r = net["b"].post(
        f"/v1/trade/inbox/{inbox[0]['id']}/reply", {"answer": "have_customer", "message": "Family of 3, can visit Sunday"}, format="json"
    )
    assert r.status_code == 200 and r.json()["reply"] == "have_customer"

    detail = net["a"].get(f"/v1/trade/blasts/{body['id']}").json()
    assert detail["replies"] == [
        {
            "from": "Om Sai Estate Agents",
            "phone": "+919820000002",
            "message": "Family of 3, can visit Sunday",
            "at": detail["replies"][0]["at"],
        }
    ]
    assert Notification.objects.filter(org_id=net["org"].pk, template="trade_reply").exists()
    # Nothing moved between inventories, and each firm sees only its own side.
    assert _listing_count(net["borg"]) == before_b
    with rls.org_context(net["borg"].pk):
        assert TradeBlast.objects.count() == 0
    with rls.org_context(net["org"].pk):
        assert TradeDelivery.objects.count() == 0


def test_requirement_blast_never_names_the_customer(net):
    r = net["a"].post("/v1/trade/blasts", {"kind": "requirement", "requirement_id": str(net["req"].pk), "scope": "all"}, format="json")
    assert r.status_code == 201, r.content
    t = r.json()["text"]
    assert t.startswith("Wanted: 2 BHK for rent in Manpada, up to ₹30,000/month.")
    assert "Priya" not in t and "9876500009" not in t
    inbox = net["b"].get("/v1/trade/inbox").json()
    assert inbox[0]["kind"] == "requirement"
    assert net["b"].post(f"/v1/trade/inbox/{inbox[0]['id']}/reply", {"answer": "have_flat"}, format="json").status_code == 200


def test_rules(net, broker_b):
    a, b = net["a"], net["b"]
    assert b.post("/v1/trade/blasts", {"kind": "flats", "listing_ids": [str(net["listing"].pk)]}, format="json").status_code == 400
    assert a.post("/v1/trade/blasts", {"kind": "flats", "listing_ids": []}, format="json").status_code == 400
    far = {"kind": "flats", "listing_ids": [str(net["listing"].pk)], "scope": "selected", "contact_ids": []}
    assert a.post("/v1/trade/blasts", far, format="json").status_code == 400
    staff_user = make_user("9820011111", "Imran")
    Membership.objects.create(user=staff_user, org=net["org"], role=Membership.Role.STAFF)
    staff = api_for(staff_user, net["org"], role="broker_staff")
    assert staff.get("/v1/trade/contacts").status_code == 403


def test_other_import_formats(net):
    vcf = b"BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Sunil Estate\r\nTEL;TYPE=CELL:+91 98203 00004\r\nORG:Sunil Estate Agency\r\nEND:VCARD\r\n"
    r = net["a"].post("/v1/trade/contacts/import", {"file": _file("contacts.vcf", vcf)}, format="multipart").json()
    assert r["added"] == 1
    r = (
        net["a"]
        .post("/v1/trade/contacts/import", {"text": "Mahesh 9820300005\nRamesh Patil, 9820300001\nno number here"}, format="json")
        .json()
    )
    assert (r["added"], r["updated"], r["skipped_count"]) == (1, 1, 1)


def _listing_count(org):
    with rls.org_context(org.pk):
        return Listing.objects.count()
