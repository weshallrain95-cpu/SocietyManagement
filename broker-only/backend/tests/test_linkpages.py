"""WhatsApp/SMS link pages for owners and offline customers."""

from datetime import date, time

import pytest
from django.test import Client
from django.utils import timezone

from apps.crm import services as crm
from apps.inventory.services import create_listing, set_keys
from apps.masterdata.models import Building, OwnershipClaim, Unit
from apps.status import services as st
from apps.status.models import StatusConfirmation, UnitStatus
from apps.visits import services as v
from common import rls
from common.crypto import token_hash
from common.models import ShareLink

from .conftest import DHOKALI, make_user

pytestmark = pytest.mark.django_db


def mint(purpose, target_id, token="tok") -> str:
    """Links store only a hash; give an existing link a known token for the test."""
    link = ShareLink.objects.filter(purpose=purpose, target_id=target_id).latest("created_at")
    link.token_hash = token_hash(token)
    link.save()
    return token


@pytest.fixture
def world(society, attrs, broker_a):
    org, user = broker_a
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    with rls.org_context(org.pk):
        listings = []
        for no, rent in (("1203", 24000), ("1204", 22000)):
            u = Unit.objects.create(building=b, unit_no=no, bhk=2, floor=12)
            l, _ = create_listing(
                org=org,
                user=user,
                unit=u,
                txn_type="RENT",
                data={"asking_rent": rent},
                owner_phone="9819000001",
                attributes={"pets_allowed": "all pets", "lift": True},
            )
            set_keys(l, holder_type="office")
            listings.append(l)
        cust, _ = crm.capture_customer(org=org, user=user, phone="9876543210", name="Riya", source="walk_in")
    return {"org": org, "user": user, "listings": listings, "customer": cust}


def test_owner_confirms_availability(world):
    unit = world["listings"][0].unit
    owner = make_user("9819000001", "Owner")
    OwnershipClaim.objects.create(unit=unit, user=owner, status="verified", verified_at=timezone.now())
    st.report(unit, "RENT", "LET", st.Actor.broker(world["org"]))
    st.report(unit, "RENT", "AVAILABLE", st.Actor.broker(world["org"]))
    token = mint("status_confirmation", StatusConfirmation.objects.get(unit=unit).pk)
    c = Client()
    r = c.get(f"/c/{token}")
    assert r.status_code == 200 and "Flat 1203, Rodas A, Hiranandani Estate" in r.content.decode()
    assert r["Referrer-Policy"] == "same-origin" and "noindex" in r["X-Robots-Tag"]
    r = c.post(f"/c/{token}", {"answer": "yes"})
    assert r.status_code == 302
    assert UnitStatus.objects.get(unit=unit, txn_type="RENT").state == "AVAILABLE"
    again = c.get(f"/c/{token}")  # reopening shows the thank-you, not an error
    assert again.status_code == 200 and "Thank you" in again.content.decode()
    assert c.post(f"/c/{token}", {"answer": "no"}).status_code == 200  # shows the thank-you again, changes nothing
    assert UnitStatus.objects.get(unit=unit, txn_type="RENT").state == "AVAILABLE"  # second answer ignored


def test_owner_available_from_needs_a_date(world):
    unit = world["listings"][0].unit
    owner = make_user("9819000002")
    OwnershipClaim.objects.create(unit=unit, user=owner, status="verified", verified_at=timezone.now())
    st.report(unit, "RENT", "LET", st.Actor.broker(world["org"]))
    st.report(unit, "RENT", "AVAILABLE", st.Actor.broker(world["org"]))
    token = mint("status_confirmation", StatusConfirmation.objects.get(unit=unit).pk)
    assert Client().post(f"/c/{token}", {"answer": "available_from"}).status_code == 400
    Client().post(f"/c/{token}", {"answer": "available_from", "available_from": "2026-11-01"})
    s = UnitStatus.objects.get(unit=unit, txn_type="RENT")
    assert s.state == "AVAILABLE" and s.available_from == date(2026, 11, 1)


def test_shortlist_page_hides_flat_numbers_and_records_interest(world):
    with rls.org_context(world["org"].pk):
        crm.request_consent(world["customer"], method="attested", user=world["user"])
        sl = crm.create_shortlist(world["customer"], world["listings"])
        token = crm.share_shortlist(sl, user=world["user"])
        item = sl.items.first()
    c = Client()
    html = c.get(f"/s/{token}").content.decode()
    assert "Hiranandani Estate" in html and "₹24,000/mo" in html and "Sent by Suresh Realty" in html
    assert "1203" not in html and "1204" not in html  # no flat numbers before a visit
    assert "9819" not in html  # never the owner's number
    r = c.post(f"/s/{token}", {"item": str(item.pk), "response": "interested"})
    assert r.status_code == 302 and "?r=1" in r["Location"]
    assert "interested — your broker" in c.get(r["Location"]).content.decode()
    with rls.org_context(world["org"].pk):
        item.refresh_from_db()
        assert item.customer_response == "interested"
        kinds = list(world["customer"].interactions.values_list("kind", flat=True))
        assert kinds.count("link_opened") == 1  # the redirect after answering is not a second 'open'


def test_visit_plan_page_confirm_then_flat_numbers_show(world):
    with rls.org_context(world["org"].pk):
        crm.request_consent(world["customer"], method="attested", user=world["user"])
        plan = v.create_plan(
            customer=world["customer"],
            listings=world["listings"],
            date=date(2026, 10, 3),
            start_time=time(11, 0),
            user=world["user"],
            start_point=DHOKALI,
        )
        token = v.share_with_customer(plan, user=world["user"])
    c = Client()
    html = c.get(f"/v/{token}").content.decode()
    assert "Sent by Suresh Realty" in html
    assert "Saturday, 3 October" in html and "11:01 AM" in html  # India time (1 min travel from the start point)
    assert "Flat 1203" not in html
    c.post(f"/v/{token}", {"action": "confirm"})
    html = c.get(f"/v/{token}").content.decode()
    assert "Confirmed" in html and "Flat 1203" in html


def test_customer_can_propose_another_time(world):
    with rls.org_context(world["org"].pk):
        crm.request_consent(world["customer"], method="attested", user=world["user"])
        plan = v.create_plan(
            customer=world["customer"], listings=world["listings"][:1], date=date(2026, 10, 3), start_time=time(11, 0), user=world["user"]
        )
        token = v.share_with_customer(plan, user=world["user"])
    assert Client().post(f"/v/{token}", {"action": "propose"}).status_code == 400
    r = Client().post(f"/v/{token}", {"action": "propose", "slot": "2026-10-04T16:30"})
    assert "done=proposed" in r["Location"]
    with rls.org_context(world["org"].pk):
        plan.refresh_from_db()
        assert timezone.localtime(plan.customer_proposed_slot).hour == 16


def test_owner_visit_notice(world):
    with rls.org_context(world["org"].pk):
        plan = v.create_plan(
            customer=world["customer"], listings=world["listings"][:1], date=date(2026, 10, 3), start_time=time(11, 0), user=world["user"]
        )
        v.notify_owners(plan)
        stop = v.live_stops(plan)[0]
    token = mint("visit_notice", stop.pk)
    c = Client()
    assert "A visit is scheduled at your flat" in c.get(f"/o/{token}").content.decode()
    c.post(f"/o/{token}", {"answer": "ok"})
    assert "the time works for you" in c.get(f"/o/{token}").content.decode()


def test_consent_page(world):
    with rls.org_context(world["org"].pk):
        token = crm.request_consent(world["customer"], method="link", user=world["user"])["token"]
    c = Client()
    assert "Can Suresh Realty send you flat details?" in c.get(f"/consent/{token}").content.decode()
    assert "Thank you" in c.post(f"/consent/{token}", {"answer": "agree"}).content.decode()
    with rls.org_context(world["org"].pk):
        world["customer"].refresh_from_db()
        assert world["customer"].consent_state == "link_confirmed"


def test_review_page(world):
    with rls.org_context(world["org"].pk):
        crm.request_consent(world["customer"], method="attested", user=world["user"])
        plan = v.create_plan(
            customer=world["customer"], listings=world["listings"][:1], date=date(2026, 10, 3), start_time=time(11, 0), user=world["user"]
        )
        stop = v.live_stops(plan)[0]
        v.check_in(stop)
        v.record_outcome(stop, "liked", user=world["user"])
    from apps.reviews.models import Interaction

    token = mint("review", Interaction.objects.get(ref_id=plan.pk).pk)
    c = Client()
    html = c.get(f"/r/{token}").content.decode()
    assert "How was your visit with Suresh Realty?" in html and "Honest listing" in html
    assert c.post(f"/r/{token}", {}).status_code == 400
    assert "Thank you" in c.post(f"/r/{token}", {"stars": "5", "tags": ["punctual"]}).content.decode()
    world["org"].refresh_from_db()
    assert world["org"].rating_count == 1


def test_bad_links_get_a_friendly_page():
    r = Client().get("/c/not-a-real-token")
    assert r.status_code == 410 and "Ask your broker to send a new one" in r.content.decode()


def test_forms_are_csrf_protected(world):
    with rls.org_context(world["org"].pk):
        token = crm.request_consent(world["customer"], method="link", user=world["user"])["token"]
    strict = Client(enforce_csrf_checks=True)
    assert strict.post(f"/consent/{token}", {"answer": "agree"}).status_code == 403
    page = strict.get(f"/consent/{token}")
    csrf = page.cookies["csrftoken"].value
    assert strict.post(f"/consent/{token}", {"answer": "agree", "csrfmiddlewaretoken": csrf}).status_code == 200


def test_link_pages_are_rate_limited():
    c = Client()
    codes = [c.get(f"/c/guess-{i}").status_code for i in range(35)]
    assert codes[0] == 410 and codes[-1] == 429


def test_messages_show_india_time_in_words(world):
    from common.models import Notification

    with rls.org_context(world["org"].pk):
        crm.request_consent(world["customer"], method="attested", user=world["user"])
        plan = v.create_plan(
            customer=world["customer"], listings=world["listings"][:1], date=date(2026, 10, 3), start_time=time(11, 0), user=world["user"]
        )
        v.share_with_customer(plan, user=world["user"])
        v.notify_owners(plan)
    notice = Notification.objects.filter(template="visit_notice").latest("created_at").payload
    assert notice["when"] == "Sat 3 Oct, 11:00 AM"
    shared = Notification.objects.filter(template="visit_plan_shared").latest("created_at").payload
    assert shared["date"] == "Sat 3 Oct"


def test_place_type_is_not_repeated():
    from apps.linkpages.views import _facts

    facts = {
        "school": {"name": "Lokpuram Public School", "distance_m": 900, "walk_min": 12, "drive_min": 5},
        "auto_stand": {"name": "Dhokali Naka", "distance_m": 80, "walk_min": 1, "drive_min": 2},
    }
    assert _facts(facts) == ["Dhokali Naka auto stand: 80 m · 1 min walk", "Lokpuram Public School: 900 m · 12 min walk"]


def test_buttons_work_with_a_real_browser_origin(world, settings):
    """Browsers send an Origin header on form posts; it must pass Django's CSRF origin check."""
    settings.ALLOWED_HOSTS = ["testserver"]
    with rls.org_context(world["org"].pk):
        token = crm.request_consent(world["customer"], method="link", user=world["user"])["token"]
    strict = Client(enforce_csrf_checks=True)
    csrf = strict.get(f"/consent/{token}").cookies["csrftoken"].value
    r = strict.post(f"/consent/{token}", {"answer": "agree", "csrfmiddlewaretoken": csrf}, HTTP_ORIGIN="http://testserver")
    assert r.status_code == 200
    # What a "no-referrer" policy would have made browsers send:
    with rls.org_context(world["org"].pk):
        token = crm.request_consent(world["customer"], method="link", user=world["user"])["token"]
    bad = Client(enforce_csrf_checks=True)
    csrf = bad.get(f"/consent/{token}").cookies["csrftoken"].value
    assert bad.post(f"/consent/{token}", {"answer": "agree", "csrfmiddlewaretoken": csrf}, HTTP_ORIGIN="null").status_code == 403
