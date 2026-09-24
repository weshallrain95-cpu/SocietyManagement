"""Owners module: register with proof, photos/videos, invite with the allow tick, remove/allow brokers, review.

Founder rules (D13/D14): inventory is built only by brokers; an owner hands a flat to a broker only after
ticking "Allow this broker to handle my property"; unticking removes any broker (invited or self-added),
who cannot re-add the flat until the owner allows them again; proof is kept but never checked.
"""

import io

import pytest
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from PIL import Image

from apps.crm import services as crm
from apps.inventory.models import Listing
from apps.inventory.services import create_listing
from apps.masterdata.models import Building, OwnershipClaim, Unit
from apps.orgs.models import BrokerOrg
from apps.owners.models import OwnerInvite, UnitMedia
from apps.reviews.models import Review
from common import rls

from .conftest import DHOKALI, api_for, make_org
from .test_api_journeys import login

pytestmark = pytest.mark.django_db


def jpeg(w=1200, h=900, *, gps=True) -> bytes:
    img = Image.new("RGB", (w, h), (180, 120, 60))
    buf = io.BytesIO()
    exif = Image.Exif()
    if gps:
        exif[0x010F] = "PhoneMaker"  # camera make
        exif[0x8825] = {2: (19.0, 15.0, 30.0)}  # GPS latitude
    img.save(buf, "JPEG", exif=exif)
    return buf.getvalue()


def upload(name, data, ctype):
    return SimpleUploadedFile(name, data, content_type=ctype)


PDF = b"%PDF-1.4 ..."
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 5000


@pytest.fixture
def rodas(society):
    return Building.objects.create(society=society, name="Rodas A", location=society.location, floors_total=20, units_per_floor=4)


@pytest.fixture
def owner(rodas, society):
    c, tokens = login("9819000001", "Mrs Kulkarni")
    r = c.post(
        "/v1/owner/flats",
        {
            "society_id": str(society.pk),
            "wing": "Rodas A",
            "unit_no": "1203",
            "bhk": "2",
            "declared": "true",
            "proof": upload("index2.jpg", jpeg(), "image/jpeg"),
        },
        format="multipart",
    )
    assert r.status_code == 201, r.content
    return c, r.json()


@pytest.fixture
def suresh(attrs):
    org, user = make_org("Suresh Realty", "9820000001")
    org.office_location = DHOKALI
    org.save()
    return org, user, api_for(user, org)


def test_register_needs_declaration_and_proof_and_respects_layout(rodas, society):
    c, _ = login("9819000002")
    base = {"society_id": str(society.pk), "wing": "Rodas A", "bhk": "2"}
    r = c.post(
        "/v1/owner/flats",
        base | {"unit_no": "1203", "declared": "false", "proof": upload("p.jpg", jpeg(), "image/jpeg")},
        format="multipart",
    )
    assert r.status_code == 400 and "confirm that you own" in r.json()["detail"]
    r = c.post(
        "/v1/owner/flats",
        base | {"unit_no": "2504", "declared": "true", "proof": upload("p.jpg", jpeg(), "image/jpeg")},
        format="multipart",
    )
    rodas.layout_verified = True
    rodas.save()
    r = c.post(
        "/v1/owner/flats",
        base | {"unit_no": "2504", "declared": "true", "proof": upload("p.jpg", jpeg(), "image/jpeg")},
        format="multipart",
    )
    assert r.status_code == 400 and "20 floors" in r.json()["detail"]  # closed universe applies to owners too
    r = c.post(
        "/v1/owner/flats",
        base | {"unit_no": "1203", "declared": "true", "proof": upload("p.pdf", PDF, "application/pdf")},
        format="multipart",
    )
    assert r.status_code == 201
    flat = r.json()
    assert flat["claim_status"] == "declared" and flat["proof_on_file"] and flat["media"] == []  # proof never listed as media


def test_owner_login_lands_in_owner_mode(owner):
    _, tokens = login("9819000001")
    assert tokens["role"] == "owner"


def test_photos_are_cleaned_and_videos_accepted(owner):
    c, flat = owner
    r = c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("a.jpg", jpeg(4000, 3000), "image/jpeg")}, format="multipart")
    assert r.status_code == 201, r.content
    p = UnitMedia.objects.get(pk=r.json()["id"])
    img = Image.open(p.file)
    assert max(img.size) == 2048 and not img.getexif()  # resized, GPS and camera details stripped
    assert p.thumb and Image.open(p.thumb).size[0] == 480
    r = c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("walk.mp4", MP4, "video/mp4")}, format="multipart")
    assert r.status_code == 201 and r.json()["kind"] == "video"
    r = c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("x.mp4", b"not a video at all", "video/mp4")}, format="multipart")
    assert r.status_code == 400
    r = c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("x.jpg", b"garbage", "image/jpeg")}, format="multipart")
    assert r.status_code == 400
    detail = c.get(f"/v1/owner/flats/{flat['id']}").json()
    assert [x["kind"] for x in detail["media"]] == ["photo", "video"]


def test_signed_links_and_range_requests(owner):
    c, flat = owner
    vid = c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("walk.mp4", MP4, "video/mp4")}, format="multipart").json()
    web = Client()
    url = vid["url"].replace("http://testserver", "")
    r = web.get(url, HTTP_RANGE="bytes=0-99")
    assert r.status_code == 206 and r["Content-Range"] == f"bytes 0-99/{len(MP4)}" and len(r.content) == 100
    assert web.get(url).status_code == 200
    assert web.get(url.replace("s=", "s=x")).status_code == 404  # tampered
    assert web.get(url.split("?")[0]).status_code == 404  # unsigned


def test_invite_needs_the_allow_tick_then_broker_accepts(owner, suresh):
    c, flat = owner
    org, user, bc = suresh
    other_org, other_user = make_org("Om Sai Estate", "9820000002")
    other_org.office_location = Point(72.8258, 18.9067, srid=4326)  # Colaba: 35 km away
    other_org.save()
    nearby = c.get(f"/v1/owner/flats/{flat['id']}/brokers").json()
    assert [b["name"] for b in nearby] == ["Suresh Realty"]  # office within 5 km; unverified or far firms not shown
    c.put(
        f"/v1/owner/flats/{flat['id']}/terms",
        {"terms": {"txn_type": "RENT", "expected_rent": 26000, "deposit": 78000}, "house_rules": {"pets_allowed": "no"}},
        format="json",
    )
    r = c.post(f"/v1/owner/flats/{flat['id']}/invite", {"org_id": str(org.pk), "allow": False}, format="json")
    assert r.status_code == 400 and "Allow this broker" in r.json()["detail"]
    r = c.post(f"/v1/owner/flats/{flat['id']}/invite", {"org_id": str(org.pk), "allow": True}, format="json")
    assert r.status_code == 201 and r.json()["allowed_at"]
    assert api_for(other_user, other_org).get("/v1/owner-invites").json() == []  # other firms never see it
    inv = bc.get("/v1/owner-invites").json()
    assert inv[0]["society"] == "Hiranandani Estate" and inv[0]["terms"]["expected_rent"] == 26000
    r = bc.post(f"/v1/owner-invites/{inv[0]['id']}/accept")
    assert r.status_code == 200
    listing = bc.get(f"/v1/listings/{r.json()['listing_id']}").json()
    assert listing["owner_appointed"] and listing["asking_rent"] == 26000 and listing["owner_phone"].endswith("19000001")
    view = c.get(f"/v1/owner/flats/{flat['id']}").json()
    b = view["brokers"][0]
    assert b["name"] == "Suresh Realty" and b["owner_appointed"] and b["allowed"] and b["contact"].endswith("20000001")
    assert view["statuses"][0]["label"].startswith("Available for rent")


def test_owner_removes_any_broker_and_decision_is_final(owner, suresh):
    c, flat = owner
    org, user, bc = suresh
    unit = Unit.objects.get(pk=flat["unit_id"])
    with rls.org_context(org.pk):  # route 2: the broker added the flat on their own
        listing, _ = create_listing(org=org, user=user, unit=unit, txn_type="RENT", data={"asking_rent": 25000})
    c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("a.jpg", jpeg(), "image/jpeg")}, format="multipart")
    assert len(bc.get(f"/v1/listings/{listing.pk}").json()["media"]) == 1  # brokers holding the flat see owner photos
    assert c.get(f"/v1/owner/flats/{flat['id']}").json()["brokers"][0]["allowed"] is True

    r = c.post(f"/v1/owner/flats/{flat['id']}/brokers/{org.pk}/allowed", {"allowed": False, "reason": "not responsive"}, format="json")
    assert r.status_code == 200 and r.json()["brokers"][0]["allowed"] is False
    detail = bc.get(f"/v1/listings/{listing.pk}").json()
    assert detail["owner_withdrew"] and detail["media"] == []
    assert bc.get("/v1/listings/search", {"q": "HE 1203"}).json()["results"] == []
    r = bc.post(
        "/v1/listings",
        {
            "society_id": str(unit.building.society_id),
            "building": "Rodas A",
            "unit_no": "1203",
            "bhk": "2",
            "txn_type": "RENT",
            "asking_rent": 25000,
        },
        format="json",
    )
    assert r.status_code == 400 and "removed your firm" in r.json()["detail"]  # cannot quietly re-add

    r = bc.post(f"/v1/listings/{listing.pk}/ask-owner-back", {"note": "Sorry, new staff member will call within the hour"}, format="json")
    assert r.status_code == 202
    assert "new staff member" in c.get(f"/v1/owner/flats/{flat['id']}").json()["brokers"][0]["asked_back"]
    c.post(f"/v1/owner/flats/{flat['id']}/brokers/{org.pk}/allowed", {"allowed": True}, format="json")
    assert bc.get(f"/v1/listings/{listing.pk}").json()["owner_withdrew"] is False


def test_owner_reviews_broker(owner, suresh):
    c, flat = owner
    org, user, _ = suresh
    unit = Unit.objects.get(pk=flat["unit_id"])
    with rls.org_context(org.pk):
        create_listing(org=org, user=user, unit=unit, txn_type="RENT", data={"asking_rent": 25000})
    r = c.post(f"/v1/owner/flats/{flat['id']}/brokers/{org.pk}/review", {"stars": 5, "text": "Found a family in a week"}, format="json")
    assert r.status_code == 201
    assert Review.objects.get(pk=r.json()["id"]).direction == "O2B"
    assert BrokerOrg.objects.get(pk=org.pk).rating_count == 1
    stranger, _ = make_org("Far Away Realty", "9820000009")
    r = c.post(f"/v1/owner/flats/{flat['id']}/brokers/{stranger.pk}/review", {"stars": 1}, format="json")
    assert r.status_code == 400


def test_other_people_cannot_touch_my_flat(owner):
    _, flat = owner
    c2, _ = login("9819000077")
    assert c2.get(f"/v1/owner/flats/{flat['id']}").status_code == 404
    assert (
        c2.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("a.jpg", jpeg(), "image/jpeg")}, format="multipart").status_code
        == 404
    )


def test_customer_link_shows_owner_photos_behind_switch(owner, suresh, settings):
    c, flat = owner
    org, user, _ = suresh
    unit = Unit.objects.get(pk=flat["unit_id"])
    c.post(f"/v1/owner/flats/{flat['id']}/media", {"file": upload("a.jpg", jpeg(), "image/jpeg")}, format="multipart")
    with rls.org_context(org.pk):
        listing, _ = create_listing(org=org, user=user, unit=unit, txn_type="RENT", data={"asking_rent": 25000})
        cust, _ = crm.capture_customer(org=org, user=user, phone="9876543210", name="Riya", source="walk_in")
        crm.request_consent(cust, method="attested", user=user)
        token = crm.share_shortlist(crm.create_shortlist(cust, [listing]), user=user)
    html = Client().get(f"/s/{token}").content.decode()
    assert 'class="photos"' in html and "/m/" in html and "1203" not in html
    settings.OB_OWNER_MEDIA_ON_CUSTOMER_LINKS = False
    assert 'class="photos"' not in Client().get(f"/s/{token}?r=1").content.decode()


def test_declared_owner_gets_availability_checks(owner):
    from apps.status.services import verified_owner

    _, flat = owner
    unit = Unit.objects.get(pk=flat["unit_id"])
    assert verified_owner(unit).display_name == "Mrs Kulkarni"
    assert OwnershipClaim.objects.get(unit=unit).status == "declared"
    assert not Listing.objects.exists() and not OwnerInvite.objects.exists()  # registering never hands the flat to anyone
