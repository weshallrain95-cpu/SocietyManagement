"""End-to-end journeys over HTTP (PRD J1-J4 + offline servicing)."""

import io

import pytest
from openpyxl import Workbook
from rest_framework.test import APIClient

from apps.identity.models import User
from apps.masterdata.models import Poi
from apps.orgs.models import Membership
from common.crypto import token_hash
from common.events import relay
from common.models import ShareLink

from .conftest import DHOKALI, THANE_STN, api_for, make_user

pytestmark = pytest.mark.django_db


def login(phone, name=""):
    c = APIClient()
    r = c.post("/v1/auth/otp/request", {"phone": phone}, format="json")
    assert r.status_code == 200, r.content
    r = c.post("/v1/auth/otp/verify", {"phone": phone, "code": r.json()["dev_code"], "display_name": name}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")
    return c, r.json()


def with_token(tokens):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return c


@pytest.fixture
def admin(db):
    u = make_user("9000000001", "Ops")
    u.is_staff = True
    u.save()
    return api_for(u)


@pytest.fixture
def suresh(society, attrs, admin):
    """A broker who signs up, is verified by ops, and sets a service area."""
    Poi.objects.create(type="rail_station", name="Thane", location=THANE_STN)
    c, _ = login("9820000101", "Suresh")
    r = c.post(
        "/v1/broker-orgs",
        {
            "name": "Suresh Realty",
            "txn_types": ["RENT"],
            "rera_agent_no": "A51700000001",
            "office_location": {"lat": DHOKALI.y, "lng": DHOKALI.x},
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    org_id = r.json()["org"]["id"]
    c = with_token(r.json()["tokens"])
    assert c.post("/v1/enquiries/00000000-0000-0000-0000-000000000000/proposals", {}, format="json").status_code in (403, 404)
    r = admin.post(f"/v1/admin-api/verifications/{org_id}", {"decision": "verified", "rera_verified": True}, format="json")
    assert r.json()["verification_status"] == "verified"
    r = c.post(
        "/v1/broker-orgs/me/service-areas",
        {"label": "Dhokali 3 km", "center": {"lat": DHOKALI.y, "lng": DHOKALI.x}, "radius_km": 3, "txn_types": ["RENT"]},
        format="json",
    )
    assert r.status_code == 201, r.content
    return c, org_id


def add_listing(c, society, unit_no, rent=24000, **attrs):
    r = c.post(
        "/v1/listings",
        {
            "society_id": str(society.pk),
            "building": "Rodas A",
            "unit_no": unit_no,
            "bhk": "2",
            "txn_type": "RENT",
            "asking_rent": rent,
            "deposit": rent * 3,
            "owner_phone": "9819000001",
            "attributes": attrs,
            "keys": {"holder_type": "office", "instructions": "Drawer 3"},
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    return r.json()


def test_broker_journey_listing_privacy_and_status(suresh, society, attrs):
    c, org_id = suresh
    r = c.get("/v1/societies/search", {"q": "hira nandani est"})
    assert r.json()["results"][0]["society_id"] == str(society.pk)
    listing = add_listing(c, society, "1203", pets_allowed="all pets", furnishing="semi-furnished")
    assert listing["status"] == "AVAILABLE_UNCONFIRMED"
    assert listing["keys"]["instructions"] == "Drawer 3"
    assert listing["attributes"]["pets_allowed"]["value"] == "all pets"

    # Another broker cannot see it, by list or by id.
    other, _ = login("9820000202", "Other")
    r = other.post("/v1/broker-orgs", {"name": "Other Realty", "txn_types": ["RENT"]}, format="json")
    other = with_token(r.json()["tokens"])
    assert other.get("/v1/listings").json() == []
    assert other.get(f"/v1/listings/{listing['id']}").status_code == 404

    r = c.post(f"/v1/listings/{listing['id']}/status", {"state": "LET", "licence_end_date": "2027-08-31"}, format="json")
    assert r.json()["state"] == "LET"
    r = c.post(f"/v1/listings/{listing['id']}/status", {"state": "AVAILABLE", "on_behalf_of_owner": True}, format="json")
    assert r.json()["state"] == "AVAILABLE"  # owner reached by phone, no verified owner on platform

    card = APIClient().get(f"/v1/units/{listing['unit_id']}").json()
    assert card["unit_no"] is None  # public card hides the flat number
    assert card["location_facts"]["rail_station"]["name"] == "Thane"


def test_offline_customer_to_visit_to_review(suresh, society, attrs):
    c, org_id = suresh
    l1 = add_listing(c, society, "1203", pets_allowed="all pets")
    l2 = add_listing(c, society, "1204", rent=22000, pets_allowed="no")
    r = c.post("/v1/customers", {"phone": "98765 43210", "name": "Riya", "source": "phone_call"}, format="json")
    cust = r.json()
    assert r.status_code == 201 and cust["consent_state"] == "none"
    r = c.post(
        f"/v1/customers/{cust['id']}/requirements",
        {
            "txn_type": "RENT",
            "bhk_min": 2,
            "bhk_max": 2,
            "budget_max": 25000,
            "center": {"lat": DHOKALI.y, "lng": DHOKALI.x},
            "radius_m": 2000,
            "house_rule_needs": {"pets": "dog"},
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    req = r.json()
    r = c.post(f"/v1/requirements/{req['id']}/match", {"include_excluded": True}, format="json").json()
    by = {m["listing"]["id"]: m for m in r["results"]}
    assert not by[l1["id"]]["excluded"] and by[l2["id"]]["excluded"]

    # Sharing needs consent; the customer consents by OTP read out on the phone.
    r = c.post(f"/v1/customers/{cust['id']}/shortlists", {"listing_ids": [l1["id"]]}, format="json")
    sl_id = r.json()["id"]
    assert c.post(f"/v1/shortlists/{sl_id}/share").status_code == 400
    code = c.post(f"/v1/customers/{cust['id']}/consent", {"method": "otp"}, format="json").json()["dev_code"]
    assert c.post(f"/v1/customers/{cust['id']}/consent/verify", {"code": code}, format="json").json()["consent_state"] == "otp_confirmed"
    assert c.post(f"/v1/shortlists/{sl_id}/share").status_code == 200
    link = ShareLink.objects.get(purpose="shortlist")
    link.token_hash = token_hash("sl-token")
    link.save()
    page = APIClient().get("/v1/public/shortlists/sl-token").json()
    assert page["broker"] == "Suresh Realty" and len(page["items"]) == 1 and "unit_no" not in page["items"][0]
    APIClient().post(f"/v1/public/shortlists/sl-token/items/{page['items'][0]['item_id']}", {"response": "interested"}, format="json")

    # Visit with a staff member who works offline.
    r = c.post("/v1/broker-orgs/me/staff", {"phone": "9820011111", "display_name": "Imran", "role": "broker_staff"}, format="json")
    staff_user = User.objects.get(pk=r.json()["user_id"])
    r = c.post(
        "/v1/visit-plans",
        {
            "customer_id": cust["id"],
            "listing_ids": [l1["id"]],
            "date": "2026-10-03",
            "start_time": "11:00",
            "start": {"lat": DHOKALI.y, "lng": DHOKALI.x},
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    plan = r.json()
    c.post(f"/v1/visit-plans/{plan['id']}/assign", {"staff_user_id": str(staff_user.pk)}, format="json")
    staff = api_for(staff_user, Membership.objects.get(user=staff_user).org, role="broker_staff")
    assert [p["id"] for p in staff.get("/v1/visit-plans").json()] == [plan["id"]]
    assert staff.post("/v1/listings", {}, format="json").status_code == 403
    assert "•" in staff.get(f"/v1/listings/{l1['id']}").json()["owner_phone"]  # masked for field staff
    assert staff.get(f"/v1/listings/{l2['id']}").status_code == 404  # not on their route
    stop = plan["stops"][0]["id"]
    r = staff.post(
        "/v1/sync",
        {
            "device_id": "imran-phone",
            "mutations": [
                {"idempotency_key": "a1", "entity": "checkin", "stop_id": stop, "client_ts": "2026-10-03T11:07:00+05:30"},
                {
                    "idempotency_key": "a2",
                    "entity": "outcome",
                    "stop_id": stop,
                    "outcome": "liked",
                    "client_ts": "2026-10-03T11:25:00+05:30",
                },
            ],
        },
        format="json",
    )
    assert [x["result"] for x in r.json()["results"]] == ["applied", "applied"]

    # Completed visit -> the offline customer reviews by link -> broker rating moves.
    link = ShareLink.objects.get(purpose="review")
    link.token_hash = token_hash("rv-token")
    link.save()
    assert APIClient().post("/v1/public/reviews/rv-token", {"stars": 5, "tags": ["punctual"]}, format="json").status_code == 201
    reviews = APIClient().get(f"/v1/brokers/{org_id}/reviews").json()
    assert reviews[0]["stars"] == 5
    timeline = c.get(f"/v1/customers/{cust['id']}/timeline").json()
    assert {"shortlist_response", "visit", "whatsapp"} <= {t["kind"] for t in timeline}


def test_marketplace_journey(suresh, society, attrs):
    c, org_id = suresh
    add_listing(c, society, "1203", pets_allowed="all pets")
    c.post("/v1/presence", {"online": True}, format="json")
    riya, _ = login("9876543210", "Riya")
    r = riya.post(
        "/v1/enquiries",
        {
            "txn_type": "RENT",
            "bhk_min": 2,
            "bhk_max": 2,
            "budget_max": 25000,
            "center": {"lat": DHOKALI.y, "lng": DHOKALI.x},
            "radius_m": 3000,
            "area_label": "Dhokali",
            "house_rule_needs": {"pets": "dog"},
            "urgency": "urgent",
        },
        format="json",
    )
    assert r.status_code == 201, r.content
    enquiry_id = r.json()["id"]
    relay()
    leads = c.get("/v1/broker/leads").json()
    assert leads[0]["id"] == enquiry_id and leads[0]["match_count"] == 1
    r = c.post(
        f"/v1/enquiries/{enquiry_id}/proposals", {"brokerage_terms": "15 days' rent", "message": "I have 1 flat that fits"}, format="json"
    )
    assert r.status_code == 201, r.content
    detail = riya.get(f"/v1/enquiries/{enquiry_id}").json()
    assert detail["proposals"][0]["broker"]["rera_registered"] is True
    r = riya.post(f"/v1/proposals/{detail['proposals'][0]['id']}/accept")
    assert r.json()["state"] == "accepted"
    customers = c.get("/v1/customers").json()
    assert customers[0]["source"] == "marketplace" and customers[0]["consent_state"] == "app"


def test_owner_confirms_by_link(suresh, society, attrs):
    from django.utils import timezone

    from apps.masterdata.models import OwnershipClaim, Unit

    c, _ = suresh
    listing = add_listing(c, society, "1203")
    owner = make_user("9819000001", "Mrs Kulkarni")
    OwnershipClaim.objects.create(unit=Unit.objects.get(pk=listing["unit_id"]), user=owner, status="verified", verified_at=timezone.now())
    c.post(f"/v1/listings/{listing['id']}/status", {"state": "LET"}, format="json")
    assert c.post(f"/v1/listings/{listing['id']}/status", {"state": "AVAILABLE"}, format="json").json()["state"] == "AVAILABLE_UNCONFIRMED"
    link = ShareLink.objects.get(purpose="status_confirmation")
    link.token_hash = token_hash("owner-token")
    link.save()
    anon = APIClient()
    assert "available for rent?" in anon.get("/v1/public/confirmations/owner-token").json()["question"]
    r = anon.post("/v1/public/confirmations/owner-token", {"response": "yes"}, format="json")
    assert r.json()["status"] == "Available for rent"
    assert anon.post("/v1/public/confirmations/owner-token", {"response": "yes"}, format="json").status_code == 410
    assert anon.get("/v1/public/confirmations/not-a-token").status_code == 410


def test_upload_over_http(suresh, society, attrs, thane):
    c, _ = suresh
    wb = Workbook()
    wb.active.append(["Society", "Flat", "BHK", "Rent"])
    wb.active.append(["Hiranandani Estate", "1601", "3", "45000"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.name = "flats.xlsx"
    buf.seek(0)
    r = c.post("/v1/uploads", {"file": buf, "micro_market_id": str(thane["mm"].pk)}, format="multipart")
    assert r.status_code == 201, r.content
    batch = r.json()
    assert batch["counts"] == {"auto": 1, "total": 1}
    assert c.post(f"/v1/uploads/{batch['id']}/commit").json()["committed"] == 1
    assert c.get("/v1/uploads/template").status_code == 200


def test_map_and_admin_endpoints(suresh, society, attrs, admin):
    c, _ = suresh
    for n in ("1203", "1204"):
        add_listing(c, society, n)
    from apps.marketplace.tasks import rebuild_supply

    rebuild_supply(force=True)
    r = APIClient().get("/v1/map/supply", {"bbox": "72.9,19.1,73.1,19.3", "zoom": 13, "txn": "RENT"})
    assert r.json()["clusters"][0]["units"] == 2
    assert c.get("/v1/admin-api/audit/verify").status_code == 403
    v = admin.get("/v1/admin-api/audit/verify").json()
    assert v["audit"]["ok"] and v["status_ledger"]["ok"]


def test_openapi_schema_builds(db):
    r = APIClient().get("/v1/schema")
    assert r.status_code == 200 and b"/v1/listings" in r.content


def test_otp_rate_limit(db):
    c = APIClient()
    for _ in range(5):
        c.post("/v1/auth/otp/request", {"phone": "9123456789"}, format="json")
    assert c.post("/v1/auth/otp/request", {"phone": "9123456789"}, format="json").status_code == 429


def test_removed_staff_loses_access_immediately(suresh):
    c, _ = suresh
    r = c.post("/v1/broker-orgs/me/staff", {"phone": "9820033333", "role": "broker_staff"}, format="json")
    m = Membership.objects.get(pk=r.json()["id"])
    staff = api_for(m.user, m.org, role="broker_staff")
    assert staff.get("/v1/visit-plans").status_code == 200
    c.delete(f"/v1/broker-orgs/me/staff/{m.pk}")
    assert staff.get("/v1/visit-plans").status_code == 401


def test_cors_allows_configured_browser_origin(db, settings):
    settings.CORS_ALLOWED_ORIGINS = ["http://localhost:8081"]
    r = APIClient().options("/v1/auth/otp/request", HTTP_ORIGIN="http://localhost:8081", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
    assert r["access-control-allow-origin"] == "http://localhost:8081"
    r = APIClient().options("/v1/auth/otp/request", HTTP_ORIGIN="https://evil.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
    assert "access-control-allow-origin" not in r


def test_wing_in_flat_number_selects_the_building(suresh, society, attrs):
    c, _ = suresh
    r = c.post(
        "/v1/listings",
        {"society_id": str(society.pk), "unit_no": "B-1502", "bhk": "2", "txn_type": "RENT", "asking_rent": 26000},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert r.json()["building"] == "B"
