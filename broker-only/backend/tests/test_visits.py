import itertools
from datetime import date, time

import pytest
from django.contrib.gis.geos import Point

from apps.crm import services as crm
from apps.inventory.services import create_listing, set_keys
from apps.masterdata.models import Building, Society, Unit
from apps.orgs.models import Membership
from apps.reviews import services as reviews
from apps.reviews.models import Interaction
from apps.status.models import UnitStatus
from apps.visits import routing
from apps.visits import services as v
from apps.visits.models import VisitStop
from common import rls
from common.crypto import token_hash
from common.models import ShareLink

from .conftest import DHOKALI, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def tour(thane, attrs, broker_a):
    """Three flats in three societies around Dhokali, deliberately entered in a bad order."""
    org, user = broker_a
    spots = [("North Tower", 72.9790, 19.2400), ("South Court", 72.9775, 19.2150), ("Middle Park", 72.9780, 19.2275)]
    listings = []
    with rls.org_context(org.pk):
        for name, lng, lat in spots:
            s = Society.objects.create(canonical_name=name, locality=thane["dhokali"], location=Point(lng, lat, srid=4326))
            b = Building.objects.create(society=s, name="A", location=s.location)
            u = Unit.objects.create(building=b, unit_no="101", bhk=2)
            listing, _ = create_listing(org=org, user=user, unit=u, txn_type="RENT", data={"asking_rent": 22000},
                                        owner_phone="9819000100")
            set_keys(listing, holder_type="office")
            listings.append(listing)
        customer, _ = crm.capture_customer(org=org, user=user, phone="9876511111", name="Riya", source="phone_call")
        crm.request_consent(customer, method="attested", user=user, note="agreed on call")
    staff = make_user("9820011111", "Imran")
    Membership.objects.create(user=staff, org=org, role=Membership.Role.STAFF)
    return {"org": org, "user": user, "listings": listings, "customer": customer, "staff": staff}


def _plan(t):
    return v.create_plan(customer=t["customer"], listings=t["listings"], date=date(2026, 10, 3), start_time=time(11, 0),
                         user=t["user"], start_point=DHOKALI)


def test_route_is_optimised_and_timed(tour):
    with rls.org_context(tour["org"].pk):
        plan = _plan(tour)
        stops = v.live_stops(plan)
        pts = [(s.listing.unit.building.location.x, s.listing.unit.building.location.y) for s in stops]
        start = (DHOKALI.x, DHOKALI.y)

        def length(order):
            path = [start] + [pts[i] for i in order]
            return sum(routing.haversine_m(a, b) for a, b in zip(path, path[1:]))

        chosen = length(range(len(pts)))
        assert chosen <= min(length(p) for p in itertools.permutations(range(len(pts)))) + 1
        # The entry order (North, South, Middle) zig-zags and must not be what we kept.
        assert [s.listing.unit.building.society.canonical_name for s in stops] != ["North Tower", "South Court", "Middle Park"]
        assert all(a.slot_end <= b.slot_start for a, b in zip(stops, stops[1:]))
        assert plan.total_travel_min > 0


def test_share_assign_and_live_change(tour):
    org = tour["org"]
    with rls.org_context(org.pk):
        plan = _plan(tour)
        token = v.share_with_customer(plan, user=tour["user"])
        assert v.assign(plan, tour["staff"]) == 3
    view = v.public_plan_view(token)
    assert [s["flat"] for s in view["stops"]] == [None, None, None]  # flat numbers hidden until confirmed
    v.customer_confirms(token)
    assert all(s["flat"] == "101" for s in v.public_plan_view(token)["stops"])
    with rls.org_context(org.pk):
        stop = v.live_stops(plan)[1]
        v.remove_stop(plan, stop)
        plan.refresh_from_db()
        assert [s.seq for s in v.live_stops(plan)] == [1, 2]
        assert plan.version >= 3


def test_outsider_cannot_be_assigned(tour):
    outsider = make_user("9820099999")
    with rls.org_context(tour["org"].pk):
        with pytest.raises(v.VisitError):
            v.assign(_plan(tour), outsider)


def test_owner_notice_and_ack(tour):
    with rls.org_context(tour["org"].pk):
        plan = _plan(tour)
        assert v.notify_owners(plan) == 3
        stop = v.live_stops(plan)[0]
    link = ShareLink.objects.filter(purpose="visit_notice", target_id=stop.pk).first()
    # Tokens are never stored; simulate the owner's click by minting a known one.
    link.token_hash = token_hash("owner-click")
    link.save()
    v.owner_acknowledges("owner-click", ok=True)
    with rls.org_context(tour["org"].pk):
        stop.refresh_from_db()
        assert stop.owner_notice == "acknowledged"


def test_offline_sync_is_idempotent_and_server_wins_on_structure(tour):
    org, staff = tour["org"], tour["staff"]
    with rls.org_context(org.pk):
        plan = _plan(tour)
        v.assign(plan, staff)
        s1, s2, s3 = v.live_stops(plan)
        v.remove_stop(plan, s3)  # broker removes a stop while staff is offline
        muts = [
            {"idempotency_key": "k1", "entity": "checkin", "stop_id": str(s1.pk), "client_ts": "2026-10-03T11:05:00+05:30", "lat": s1.listing.unit.building.location.y, "lng": s1.listing.unit.building.location.x},
            {"idempotency_key": "k2", "entity": "outcome", "stop_id": str(s1.pk), "outcome": "liked", "client_ts": "2026-10-03T11:20:00+05:30"},
            {"idempotency_key": "k3", "entity": "outcome", "stop_id": str(s3.pk), "outcome": "rejected", "client_ts": "2026-10-03T12:00:00+05:30"},
        ]
        res = v.apply_mutations(org_id=org.pk, user=staff, device_id="phone-1", mutations=muts)
        assert [r["result"] for r in res] == ["applied", "applied", "conflict"]
        assert res[2]["detail"]["reason"] == "stop_removed_by_broker"
        again = v.apply_mutations(org_id=org.pk, user=staff, device_id="phone-1", mutations=muts[:2])
        assert [r["result"] for r in again] == ["duplicate", "duplicate"]
        s1.refresh_from_db()
        assert s1.outcome == "liked" and s1.checkin_at.hour == 5 and s1.checkin_distance_m < 5  # device time kept (UTC)


def test_already_let_at_visit_downgrades_master_status(tour):
    with rls.org_context(tour["org"].pk):
        plan = _plan(tour)
        stop = v.live_stops(plan)[0]
        v.check_in(stop)
        v.record_outcome(stop, VisitStop.Outcome.ALREADY_LET, user=tour["user"])
    assert UnitStatus.objects.get(unit=stop.listing.unit, txn_type="RENT").state == "LET"


def test_completed_visit_unlocks_offline_review(tour):
    org = tour["org"]
    with rls.org_context(org.pk):
        plan = _plan(tour)
        for s in v.live_stops(plan):
            v.check_in(s)
            v.record_outcome(s, "liked", user=tour["user"])
        plan.refresh_from_db()
        assert plan.state == "completed"
    inter = Interaction.objects.get(ref_id=plan.pk)
    link = ShareLink.objects.get(purpose="review", target_id=inter.pk)
    link.token_hash = token_hash("review-click")
    link.save()
    r = reviews.review_via_link("review-click", stars=5, tags=["punctual", "honest_listing"], text="Very organised")
    assert r.verified_offline
    org.refresh_from_db()
    assert org.rating_count == 1 and float(org.rating_bayes) == pytest.approx(4.17, abs=0.01)
    with pytest.raises(Exception):
        reviews.review_via_link("review-click", stars=1)


def test_key_warnings(tour):
    with rls.org_context(tour["org"].pk):
        set_keys(tour["listings"][0], holder_type="owner")
        issues = {i["issue"] for i in v.key_conflicts(_plan(tour))}
        assert "key_with_owner" in issues
