"""One agency, three kinds of people (founder decisions 2026-09-25): Admin does everything; a manager runs the
day but uploads, blasts and adding field staff only when the Admin switches them on; field staff see their
trips and can capture walk-ins. One phone number belongs to one agency."""

from datetime import date, time

import pytest

from apps.crm import services as crm
from apps.inventory.services import create_listing
from apps.masterdata.models import Building, Unit
from apps.orgs.models import Membership
from apps.visits import services as v
from common import rls
from common.models import Notification

from .conftest import DHOKALI, api_for, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def team(broker_a):
    org, admin = broker_a
    mgr = make_user("9820011111", "Meena Manager")
    staff = make_user("9820012222", "Sunil Staff")
    m_mgr = Membership.objects.create(user=mgr, org=org, role="broker_manager")
    m_staff = Membership.objects.create(user=staff, org=org, role="broker_staff")
    return {
        "org": org,
        "admin": api_for(admin, org),
        "admin_user": admin,
        "mgr": api_for(mgr, org, role="broker_manager"),
        "mgr_user": mgr,
        "m_mgr": m_mgr,
        "staff": api_for(staff, org, role="broker_staff"),
        "staff_user": staff,
        "m_staff": m_staff,
    }


def test_manager_switches_are_off_by_default_and_the_admin_turns_them_on(team):
    mgr = team["mgr"]
    assert mgr.post("/v1/customers/import", {"text": "Riya 9876543210"}, format="json").status_code == 403
    assert mgr.get("/v1/broadcasts/preview").status_code == 403
    assert mgr.get("/v1/trade/blasts/preview", {"kind": "flats"}).status_code == 403
    assert mgr.post("/v1/broker-orgs/me/staff", {"phone": "9820013333", "role": "broker_staff"}, format="json").status_code == 403
    assert mgr.get("/v1/me").json()["memberships"][0]["can"] == []

    # Only the Admin flips switches, and only for managers.
    url = f"/v1/broker-orgs/me/staff/{team['m_mgr'].pk}/permissions"
    assert mgr.put(url, {"permissions": ["uploads"]}, format="json").status_code == 403
    assert (
        team["admin"]
        .put(f"/v1/broker-orgs/me/staff/{team['m_staff'].pk}/permissions", {"permissions": ["uploads"]}, format="json")
        .status_code
        == 400
    )
    r = team["admin"].put(url, {"permissions": ["uploads", "add_staff"]}, format="json")
    assert r.status_code == 200 and r.json()["permissions"] == ["uploads", "add_staff"]

    assert mgr.post("/v1/customers/import", {"text": "Riya 9876543210"}, format="json").status_code == 200
    assert mgr.post("/v1/broker-orgs/me/staff", {"phone": "9820013333", "role": "broker_staff"}, format="json").status_code == 201
    assert mgr.post("/v1/broker-orgs/me/staff", {"phone": "9820014444", "role": "broker_manager"}, format="json").status_code == 403
    assert mgr.get("/v1/broadcasts/preview").status_code == 403  # blasts still off
    assert sorted(mgr.get("/v1/me").json()["memberships"][0]["can"]) == ["add_staff", "uploads"]
    assert sorted(team["admin"].get("/v1/me").json()["memberships"][0]["can"]) == ["add_staff", "blasts", "uploads"]


def test_who_can_remove_whom_and_agency_settings(team):
    mgr, admin = team["mgr"], team["admin"]
    other_mgr = Membership.objects.create(user=make_user("9820015555"), org=team["org"], role="broker_manager")
    assert mgr.delete(f"/v1/broker-orgs/me/staff/{other_mgr.pk}").status_code == 403
    assert mgr.delete(f"/v1/broker-orgs/me/staff/{team['m_staff'].pk}").status_code == 403  # add_staff is off
    assert admin.delete(f"/v1/broker-orgs/me/staff/{other_mgr.pk}").status_code == 200
    assert mgr.patch("/v1/broker-orgs/me", {"name": "Renamed"}, format="json").status_code == 403
    area = {"center": {"lat": DHOKALI.y, "lng": DHOKALI.x}, "radius_km": 3, "txn_types": ["RENT"]}
    assert mgr.post("/v1/broker-orgs/me/service-areas", area, format="json").status_code == 403
    assert admin.post("/v1/broker-orgs/me/service-areas", area, format="json").status_code == 201


def test_one_phone_number_one_agency(team, broker_b):
    r = team["admin"].post("/v1/broker-orgs/me/staff", {"phone": "9820000002", "role": "broker_staff"}, format="json")  # broker B's Admin
    assert r.status_code == 400 and "another agency" in r.json()["detail"]
    r = team["staff"].post("/v1/broker-orgs", {"name": "Sunil Realty", "txn_types": ["RENT"]}, format="json")
    assert r.status_code == 400 and "one agency only" in r.json()["detail"]


def test_field_staff_capture_walk_ins_but_not_other_customers(team):
    staff = team["staff"]
    with rls.org_context(team["org"].pk):
        crm.capture_customer(org=team["org"], user=team["admin_user"], phone="9876500000", name="Existing")
    r = staff.post("/v1/customers", {"phone": "9876511111", "name": "Walk-in Anil"}, format="json")
    assert r.status_code == 201
    cid = r.json()["id"]
    assert [c["name"] for c in staff.get("/v1/customers").json()] == ["Walk-in Anil"]
    r = staff.post(
        f"/v1/customers/{cid}/requirements", {"txn_type": "RENT", "bhk_min": 2, "bhk_max": 2, "budget_max": 30000}, format="json"
    )
    assert r.status_code == 201
    r = staff.post("/v1/customers", {"phone": "9876500000"}, format="json")
    assert r.status_code == 409 and "Existing" not in r.content.decode()


def test_manager_assigns_a_trip_at_once_and_the_admin_is_told(team, society, attrs):
    org, admin = team["org"], team["admin_user"]
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    with rls.org_context(org.pk):
        l, _ = create_listing(
            org=org, user=admin, unit=Unit.objects.create(building=b, unit_no="1203", bhk=2), txn_type="RENT", data={"asking_rent": 24000}
        )
        cust, _ = crm.capture_customer(org=org, user=admin, phone="9876543210", name="Riya")
        plan = v.create_plan(customer=cust, listings=[l], date=date(2026, 10, 3), start_time=time(11, 0), user=admin, start_point=DHOKALI)
    r = team["mgr"].post(f"/v1/visit-plans/{plan.pk}/assign", {"staff_user_id": str(team["staff_user"].pk)}, format="json")
    assert r.status_code == 200
    assert Notification.objects.filter(user=team["staff_user"], template="visit_assigned").exists()  # no waiting
    told = Notification.objects.get(user=admin, template="visit_assigned_by_manager")
    assert "Meena Manager gave 1 visit" in told.payload["summary"] and "Sunil Staff" in told.payload["summary"]
    team["admin"].post(f"/v1/visit-plans/{plan.pk}/assign", {"staff_user_id": str(team["staff_user"].pk)}, format="json")
    assert Notification.objects.filter(user=admin, template="visit_assigned_by_manager").count() == 1  # not for the Admin's own


def test_register_agency_makes_you_admin(db):
    c = api_for(make_user("9820099999", "New Broker"))
    r = c.post("/v1/broker-orgs", {"name": "New Realty", "txn_types": ["RENT"]}, format="json")
    assert r.status_code == 201 and r.json()["tokens"]["role"] == "broker_principal"
