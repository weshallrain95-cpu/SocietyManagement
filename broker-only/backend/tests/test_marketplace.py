from datetime import timedelta

import pytest
from django.contrib.gis.geos import MultiPolygon, Point
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.crm.models import Customer, Requirement
from apps.inventory.services import create_listing
from apps.marketplace import presence, supply
from apps.marketplace import services as mkt
from apps.marketplace.models import EnquiryDelivery
from apps.masterdata.models import Building, Unit
from apps.orgs.models import Membership, ServiceArea
from apps.orgs.serializers import circle
from common import rls
from common.events import relay
from common.models import Notification

from .conftest import DHOKALI, api_for, make_org, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def market(society, attrs, broker_a, broker_b):
    far_org, _ = make_org("Vashi Homes", "9820000009")
    pending_org, _ = make_org("New Broker", "9820000010", verified=False)
    for org in (broker_a[0], broker_b[0], pending_org):
        ServiceArea.objects.create(org=org, area=MultiPolygon(circle(DHOKALI, 3), srid=4326), txn_types=["RENT"])
    ServiceArea.objects.create(org=far_org, area=MultiPolygon(circle(Point(72.998, 19.077, srid=4326), 3), srid=4326), txn_types=["RENT"])
    org_a, user_a = broker_a
    b = Building.objects.create(society=society, name="B", location=society.location)
    with rls.org_context(org_a.pk):
        for i in range(6):
            u = Unit.objects.create(building=b, unit_no=f"{i + 1}01", bhk=2)
            create_listing(
                org=org_a,
                user=user_a,
                unit=u,
                txn_type="RENT",
                data={"asking_rent": 20000 + i * 1000},
                attributes={"pets_allowed": "all pets"},
            )
    presence.heartbeat(org_a.pk, user_a.pk)
    riya = make_user("9876543210", "Riya")
    return {"far": far_org, "pending": pending_org, "riya": riya}


def _enquiry(user, **kw):
    data = {
        "txn_type": "RENT",
        "bhk_min": 2,
        "bhk_max": 2,
        "budget_max": 25000,
        "center": DHOKALI,
        "radius_m": 3000,
        "area_label": "Dhokali",
        "house_rule_needs": {"pets": "dog"},
        "must_haves": {"furn_gas_stove": True},
        "urgency": "urgent",
    }
    data.update(kw)
    return mkt.create_enquiry(user, data)


def test_summary_reads_like_the_brief(market):
    e = _enquiry(market["riya"])
    assert e.summary_text.startswith("2 BHK on rent, urgent, around Dhokali (3 km), up to ₹25,000/month, pets")
    assert "gas stove" in e.summary_text


def test_broadcast_reaches_only_eligible_brokers_with_their_own_counts(market, broker_a, broker_b):
    e = _enquiry(market["riya"])
    relay()
    deliveries = {d.org_id: d for d in EnquiryDelivery.objects.filter(enquiry=e)}
    assert set(deliveries) == {broker_a[0].pk, broker_b[0].pk}  # not the far or unverified broker
    assert deliveries[broker_a[0].pk].match_count == 6 and deliveries[broker_a[0].pk].channel == "ws"
    assert deliveries[broker_b[0].pk].match_count == 0 and deliveries[broker_b[0].pk].channel == "push"
    n = Notification.objects.get(org=broker_b[0], template="enquiry_new")
    assert "phone" not in str(n.payload).lower()  # no customer contact before acceptance


def test_broker_who_goes_offline_gets_no_enquiries_until_back_online(market, broker_a, broker_b):
    org_b, user_b = broker_b
    c = api_for(user_b, org_b)
    assert c.get("/v1/presence").json() == {"online": True}  # online from sign-up
    assert c.post("/v1/presence", {"online": False}, format="json").json() == {"online": False}
    assert c.get("/v1/presence").json() == {"online": False}  # remembered, not reset by the app
    assert AuditEvent.objects.filter(action="broker_org.offline").exists()
    view = supply.map_view(bbox=(72.90, 19.15, 73.05, 19.30), zoom=13, txn_type="RENT")
    assert [b["name"] for b in view["brokers_online"]] == ["Suresh Realty"]
    e = _enquiry(market["riya"])
    relay()
    assert set(EnquiryDelivery.objects.filter(enquiry=e).values_list("org_id", flat=True)) == {broker_a[0].pk}
    c.post("/v1/presence", {"online": True}, format="json")
    _enquiry(market["riya"])
    relay()
    assert EnquiryDelivery.objects.filter(org=org_b).exists()


def test_field_staff_cannot_take_the_agency_offline(broker_a):
    org, _ = broker_a
    staff = make_user("9820010001")
    Membership.objects.create(user=staff, org=org, role="broker_staff")
    c = api_for(staff, org, role="broker_staff")
    assert c.post("/v1/presence", {"online": False}, format="json").status_code == 403
    assert c.get("/v1/presence").json() == {"online": True}


def test_proposal_accept_flow_creates_crm_customer(market, broker_a, broker_b):
    e = _enquiry(market["riya"])
    relay()
    pa = mkt.send_proposal(broker_a[0], broker_a[1], e, brokerage_terms="15 days' rent")
    pb = mkt.send_proposal(broker_b[0], broker_b[1], e, brokerage_terms="1 month rent")
    with pytest.raises(mkt.MarketError):
        mkt.send_proposal(broker_a[0], broker_a[1], e, brokerage_terms="again")
    with pytest.raises(mkt.MarketError):
        mkt.send_proposal(market["far"], None, e, brokerage_terms="x")
    mkt.accept_proposal(market["riya"], pa)
    e.refresh_from_db()
    assert e.state == "in_progress"
    with rls.org_context(broker_a[0].pk):
        c = Customer.objects.get()
        assert c.source == "marketplace" and c.consent_state == "app" and c.platform_user == market["riya"]
        req = Requirement.objects.get(customer=c)
        assert req.house_rule_needs == {"pets": "dog"}
    with rls.org_context(broker_b[0].pk):
        assert not Customer.objects.exists()
    pb.refresh_from_db()
    assert pb.state == "sent"


def test_enquiry_limits_and_moderation(market):
    for _ in range(3):
        _enquiry(market["riya"])
    with pytest.raises(mkt.MarketError):
        _enquiry(market["riya"])
    other = make_user("9876543299")
    with pytest.raises(mkt.MarketError):
        _enquiry(other, notes="Community only please")


def test_supply_map_is_anonymous(market, broker_a):
    with rls.platform_context():
        supply.rebuild()
    view = supply.map_view(bbox=(72.90, 19.15, 73.05, 19.30), zoom=13, txn_type="RENT")
    [cluster] = view["clusters"]
    assert cluster["units"] == 6 and cluster["brokers_serving"] == 3 - 1  # pending broker not counted
    assert cluster["price_band"]["p25"] >= 20000
    # Online from sign-up, whether or not the app is open right now (MKT-11).
    assert sorted(b["name"] for b in view["brokers_online"]) == ["Om Sai Estate Agents", "Suresh Realty"]
    assert "listing" not in str(view).lower()


def test_price_band_hidden_below_k_anonymity(society, attrs, broker_a):
    org, user = broker_a
    b = Building.objects.create(society=society, name="Solo", location=society.location)
    with rls.org_context(org.pk):
        create_listing(
            org=org, user=user, unit=Unit.objects.create(building=b, unit_no="1", bhk=1), txn_type="RENT", data={"asking_rent": 15000}
        )
    with rls.platform_context():
        supply.rebuild()
    [cluster] = supply.map_view(bbox=(72.90, 19.15, 73.05, 19.30), zoom=13, txn_type="RENT")["clusters"]
    assert cluster["units"] == 1 and cluster["price_band"] is None


def test_expiry(market):
    e = _enquiry(market["riya"])
    assert mkt.expire_enquiries(now=timezone.now() + timedelta(days=15)) == 1
    e.refresh_from_db()
    assert e.state == "expired"
