"""First-time broker registration: the full business form (founder decision 2026-09-25)."""

import pytest

from apps.orgs.models import BrokerOrg, Membership
from apps.orgs.validators import gstin_check_char
from common.models import ReviewQueueItem

from .conftest import agency_form, api_for, make_user
from .test_api_journeys import with_token

pytestmark = pytest.mark.django_db

PAN_PERSON = "ABCPS1234K"


def gstin(pan, state="27"):
    first = f"{state}{pan}1Z"
    return first + gstin_check_char(first)


@pytest.fixture
def newbie(thane):
    return api_for(make_user("9820088888", "Ravi Shah")), thane["dhokali"]


def test_register_proprietorship(newbie):
    c, loc = newbie
    r = c.post(
        "/v1/broker-orgs",
        agency_form("Shah Realty", loc, gst_registered=True, gstin=gstin(PAN_PERSON), contact_email="ravi@example.com"),
        format="json",
    )
    assert r.status_code == 201, r.content
    org = r.json()["org"]
    assert org["pan_masked"] == "ABC*****4K" and "pan" not in org  # never sent back in full
    assert org["owners"] == [{"name": "Shah Realty Owner", "role": "Proprietor"}]
    assert org["verification_status"] == "pending" and org["declared_at"]
    assert [a["label"] for a in org["service_areas"]] == ["Dhokali"]  # new agencies can receive enquiries
    db = BrokerOrg.objects.get(pk=org["id"])
    assert db.pan_enc and PAN_PERSON.encode() not in bytes(db.pan_enc)
    assert db.office_location.equals(loc.centroid) and db.office_state == "Maharashtra"
    assert Membership.objects.get(org=db).role == "broker_principal"


@pytest.mark.parametrize(
    ("over", "field", "says"),
    [
        ({"pan": "ABCCS1234K"}, "pan", "belongs to a company"),  # company PAN on a proprietorship
        ({"pan": "12345"}, "pan", "ABCDE1234F"),
        ({"ownership_type": "partnership", "pan": "ABCFS1234K"}, "owners", "at least 2"),
        ({"gst_registered": True}, "gstin", "Enter the GSTIN"),
        ({"gst_registered": True, "gstin": gstin(PAN_PERSON)[:-1] + "0"}, "gstin", "typo"),
        ({"gst_registered": True, "gstin": gstin("ZZZPS9999Z")}, "gstin", "does not contain"),
        ({"txn_types": ["RENT", "SALE_NEW"]}, "rera_agent_no", "needed to sell new projects"),
        ({"rera_agent_no": "12345"}, "rera_agent_no", "A51700012345"),
        ({"declaration": False}, "declaration", "confirm"),
        ({"service_locality_ids": []}, "service_locality_ids", "at least one area"),
        ({"office_pincode": "4006"}, "office_pincode", "6 digits"),
        ({"legal_name": ""}, "legal_name", "needed"),
    ],
)
def test_registration_checks(newbie, over, field, says):
    c, loc = newbie
    r = c.post("/v1/broker-orgs", agency_form("Shah Realty", loc, **over), format="json")
    assert r.status_code == 400
    assert says in str(r.json()[field]), r.json()


def test_llp_with_two_designated_partners(newbie):
    c, loc = newbie
    form = agency_form(
        "Shah Associates",
        loc,
        ownership_type="llp",
        pan="ABCFS1234K",
        company_reg_no="AAB-1234",
        owners=[{"name": "Ravi Shah"}, {"name": "Meera Shah"}],
    )
    r = c.post("/v1/broker-orgs", form, format="json")
    assert r.status_code == 201, r.content
    assert {o["role"] for o in r.json()["org"]["owners"]} == {"Designated partner"}


def test_admin_edits_and_ops_rechecks_after_verification(newbie):
    c, loc = newbie
    r = c.post("/v1/broker-orgs", agency_form("Shah Realty", loc), format="json")
    admin = with_token(r.json()["tokens"])
    org = BrokerOrg.objects.get(pk=r.json()["org"]["id"])
    org.verification_status = "verified"
    org.save()
    r = admin.patch("/v1/broker-orgs/me", {"office_address": "Office 12, New Building"}, format="json")
    assert r.status_code == 200 and not ReviewQueueItem.objects.filter(kind="broker_details_changed").exists()
    r = admin.patch("/v1/broker-orgs/me", {"legal_name": "Ravi Shah HUF"}, format="json")
    assert r.status_code == 200
    item = ReviewQueueItem.objects.get(kind="broker_details_changed")
    assert "legal_name" in item.summary
    org.refresh_from_db()
    assert org.verification_status == "verified"  # keeps working while ops re-checks

    mgr = make_user("9820088899")
    Membership.objects.create(user=mgr, org=org, role="broker_manager")
    assert api_for(mgr, org, role="broker_manager").patch("/v1/broker-orgs/me", {"name": "X"}, format="json").status_code == 403


def test_ops_sees_the_business_details_and_same_pan(newbie, thane):
    from django.test import Client

    c, loc = newbie
    c.post("/v1/broker-orgs", agency_form("Shah Realty", loc), format="json")
    other = api_for(make_user("9820088877", "Copy"))
    other.post("/v1/broker-orgs", agency_form("Copy Realty", loc), format="json")  # same PAN
    staff = make_user("9000000002", "Ops")
    staff.is_staff = True
    staff.save()
    ops = Client()
    ops.force_login(staff)
    page = ops.get("/ops/brokers").content.decode()
    assert "Proprietorship" in page and "Proprietor: Shah Realty Owner" in page
    assert "ABC*****4K" in page and PAN_PERSON not in page
    assert "same PAN as Copy Realty" in page and "Serves: Dhokali" in page
