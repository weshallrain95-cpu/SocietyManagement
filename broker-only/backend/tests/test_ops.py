"""Ops console (/ops/) and applying the pilot broker's pin review."""

import json

import pytest
from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import Client

from apps.audit.models import AuditEvent
from apps.masterdata.models import Building, Society, SocietyAlias
from apps.masterdata.services import parse_maps_link, propose_society
from apps.orgs.models import BrokerOrg
from common.models import ReviewQueueItem
from common.notify import queue_for_admin

from .conftest import DHOKALI, make_org, make_user

pytestmark = pytest.mark.django_db


@pytest.fixture
def staff():
    u = make_user("9000000009", "Ops Asha")
    u.is_staff = True
    u.set_password("ops-password-123")
    u.save()
    c = Client()
    c.force_login(u)
    return c


def test_ops_requires_staff_login(broker_a):
    c = Client()
    r = c.get("/ops/")
    assert r.status_code == 302 and r["Location"].startswith("/ops/login")
    _, user = broker_a
    c.force_login(user)
    assert c.get("/ops/").status_code == 403


def test_staff_can_sign_in_with_phone_and_password(staff):
    r = Client().post("/ops/login", {"username": "9000000009", "password": "ops-password-123"})
    assert r.status_code == 302 and r["Location"] == "/ops/"


def test_every_page_renders(staff, society):
    Building.objects.create(society=society, name="Rodas A", location=society.location)
    for path in (
        "/ops/",
        "/ops/brokers",
        "/ops/queue",
        "/ops/societies?q=hiranandni",
        "/ops/map",
        "/ops/audit",
        f"/ops/societies/{society.pk}",
    ):
        r = staff.get(path)
        assert r.status_code == 200, path
        assert r["Cache-Control"] == "no-store"
    assert "Hiranandani Estate" in staff.get("/ops/societies?q=hiranandni").content.decode()


def test_verify_and_reject_broker(staff):
    org, _ = make_org("New Realty", "9820000077", verified=False)
    org.rera_agent_no = "A51700012345"
    org.save()
    assert "New Realty" in staff.get("/ops/brokers").content.decode()
    # rejecting needs a reason
    staff.post(f"/ops/brokers/{org.pk}/decide", {"decision": "rejected"})
    assert BrokerOrg.objects.get(pk=org.pk).verification_status == "pending"
    staff.post(f"/ops/brokers/{org.pk}/decide", {"decision": "verified", "rera_verified": "1"})
    org.refresh_from_db()
    assert org.verification_status == "verified" and org.rera_verified_at is not None
    assert AuditEvent.objects.filter(action="broker_org.verified", target_id=str(org.pk)).exists()


def test_provisional_society_merge_from_queue(staff, society, thane, broker_a):
    org, user = broker_a
    dup = propose_society(name="Hiranandani Estates", locality=thane["dhokali"], location=DHOKALI, org=org, user=user)
    item = ReviewQueueItem.objects.get(kind="provisional_society", ref_id=str(dup.pk))
    page = staff.get("/ops/queue").content.decode()
    assert "Same place — merge" in page and str(society.pk) in page
    r = staff.post(f"/ops/queue/{item.pk}", {"action": "merge", "into": str(society.pk)})
    assert r.status_code == 302
    dup.refresh_from_db()
    item.refresh_from_db()
    assert dup.status == "merged" and dup.merged_into_id == society.pk
    assert item.state == "resolved" and item.resolved_by is not None


def test_bad_merge_target_is_a_message_not_a_crash(staff, thane, broker_a):
    org, user = broker_a
    s = propose_society(name="Brand New Heights", locality=thane["dhokali"], location=DHOKALI, org=org, user=user)
    item = ReviewQueueItem.objects.get(ref_id=str(s.pk))
    r = staff.post(f"/ops/queue/{item.pk}", {"action": "merge", "into": "not-a-uuid"}, follow=True)
    assert "Pick a society" in r.content.decode()
    assert ReviewQueueItem.objects.get(pk=item.pk).state == "open"
    staff.post(f"/ops/queue/{item.pk}", {"action": "approve"})
    assert Society.objects.get(pk=s.pk).status == "active"


def test_move_pin_by_pasting_google_maps_link(staff, society):
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    link = "https://www.google.com/maps/place/Rodas/@19.2301234,72.9712345,17z/data=!3m1"
    staff.post(f"/ops/societies/{society.pk}", {"action": "pin", "link": link})
    society.refresh_from_db()
    b.refresh_from_db()
    assert round(society.location.y, 5) == 19.23012 and round(society.location.x, 5) == 72.97123
    assert b.location.equals_exact(society.location, tolerance=1e-7)
    # an unreadable link changes nothing
    r = staff.post(f"/ops/societies/{society.pk}", {"action": "pin", "link": "https://maps.app.goo.gl/abc"}, follow=True)
    assert "Couldn’t read a location" in r.content.decode()


def test_aliases_added_and_removed(staff, society):
    staff.post(f"/ops/societies/{society.pk}", {"action": "add_alias", "alias": "HE Complex"})
    a = SocietyAlias.objects.get(society=society, alias_raw="HE Complex")
    staff.post(f"/ops/societies/{society.pk}", {"action": "remove_alias", "alias_id": str(a.pk)})
    assert not SocietyAlias.objects.filter(pk=a.pk).exists()


def test_resolve_generic_item(staff, society):
    item = queue_for_admin("status_conflict", society, "Owner says let, broker says available")
    staff.post(f"/ops/queue/{item.pk}", {"action": "resolve", "note": "Called owner"})
    item.refresh_from_db()
    assert item.state == "resolved" and item.resolution == "Called owner"


def test_audit_page_reports_intact_chains(staff, society):
    assert "intact" in staff.get("/ops/audit").content.decode()


@pytest.mark.parametrize(
    "text,ok",
    [
        ("https://www.google.com/maps/@19.2003,72.9781,15z", True),
        ("https://maps.google.com/?q=19.2003,72.9781", True),
        ("19.2003, 72.9781", True),
        ("72.9781, 19.2003", False),  # swapped
        ("https://maps.app.goo.gl/xyz", False),
        ("", False),
    ],
)
def test_parse_maps_link(text, ok):
    p = parse_maps_link(text)
    assert (p is not None) == ok
    if ok:
        assert (round(p.y, 4), round(p.x, 4)) == (19.2003, 72.9781)


def test_apply_pin_review(tmp_path, society, thane):
    other = Society.objects.create(canonical_name="Lodha Amara", locality=thane["dhokali"], location=Point(72.99, 19.23, srid=4326))
    lost = Society.objects.create(canonical_name="Rustomjee Urbania", locality=thane["dhokali"], location=Point(72.98, 19.22, srid=4326))
    docs = {
        "hiranandani-estate": {"society": "Hiranandani Estate", "status": "correct", "aliases": "HE, Hira Estate"},
        "lodha-amara": {"society": "Lodha Amara", "status": "wrong", "link": "https://www.google.com/maps/@19.2345,72.9876,17z"},
        "rustomjee-urbania": {"society": "Rustomjee Urbania", "status": "wrong", "link": "https://maps.app.goo.gl/short"},
        "nowhere": {"society": "Nowhere Towers", "status": "correct"},
    }
    for k, v in docs.items():
        (tmp_path / f"{k}.json").write_text(json.dumps(v))

    call_command("apply_pin_review", str(tmp_path), "--dry-run")
    other.refresh_from_db()
    assert round(other.location.y, 4) == 19.23  # dry run changed nothing

    call_command("apply_pin_review", str(tmp_path))
    society.refresh_from_db()
    other.refresh_from_db()
    assert society.provenance.get("verified") is True
    assert SocietyAlias.objects.filter(society=society, alias_raw="Hira Estate").exists()
    assert (round(other.location.y, 4), round(other.location.x, 4)) == (19.2345, 72.9876)
    assert ReviewQueueItem.objects.filter(kind="pin_correction", ref_id=str(lost.pk)).exists()
