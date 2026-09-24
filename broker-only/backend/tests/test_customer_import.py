"""CRM-11 / founder point 1C: the broker's whole existing customer list comes in at once, and one message
can carry several new flats to all of it."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.crm.models import Customer
from apps.inventory.services import create_listing
from apps.masterdata.models import Building, Unit
from common import rls

from .conftest import api_for
from .test_api_journeys import login

pytestmark = pytest.mark.django_db

XLSX_ROWS = [
    ("Client Name", "Mobile No", "Remarks"),
    ("Riya", 9876543210, "2 BHK Manpada"),
    ("Karan", "98765 00001", ""),
    ("Nobody", "123", ""),
]


def _xlsx():
    import io

    from openpyxl import Workbook

    wb = Workbook()
    for r in XLSX_ROWS:
        wb.active.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return SimpleUploadedFile("customers.xlsx", buf.getvalue())


def test_import_excel_then_paste(broker_a):
    org, user = broker_a
    c = api_for(user, org)
    r = c.post("/v1/customers/import", {"file": _xlsx()}, format="multipart")
    assert r.status_code == 200, r.content
    assert (r.json()["added"], r.json()["already_in_book"], r.json()["skipped_count"]) == (2, 0, 1)
    r = c.post("/v1/customers/import", {"text": "Karan 9876500001\nMeera +91 98765 00002"}, format="json").json()
    assert (r["added"], r["already_in_book"]) == (1, 1)
    with rls.org_context(org.pk):
        riya = Customer.objects.get(name="Riya")
        assert riya.source == "import" and riya.notes == "2 BHK Manpada" and Customer.objects.count() == 3


def test_several_flats_in_one_message(society, attrs, broker_a):
    org, user = broker_a
    b = Building.objects.create(society=society, name="Rodas A", location=society.location)
    with rls.org_context(org.pk):
        l1, _ = create_listing(
            org=org, user=user, unit=Unit.objects.create(building=b, unit_no="1203", bhk=2), txn_type="RENT", data={"asking_rent": 24000}
        )
        l2, _ = create_listing(
            org=org, user=user, unit=Unit.objects.create(building=b, unit_no="504", bhk=1), txn_type="RENT", data={"asking_rent": 16000}
        )
    c = api_for(user, org)
    c.post("/v1/customers/import", {"text": "Riya 9876543210"}, format="json")
    riya, _ = login("9876543210")
    ids = [str(l1.pk), str(l2.pk)]
    p = c.get("/v1/broadcasts/preview", {"kind": "new_flat", "listing_ids": ",".join(ids)}).json()
    assert p["text"].splitlines()[:3] == [
        "New flats with Suresh Realty:",
        "• 2 BHK for rent in Hiranandani Estate, Dhokali — ₹24,000/month",
        "• 1 BHK for rent in Hiranandani Estate, Dhokali — ₹16,000/month",
    ]
    r = c.post("/v1/broadcasts", {"kind": "new_flat", "listing_ids": ids}, format="json")
    assert r.status_code == 201, r.content
    assert r.json()["listing_ids"] == ids and r.json()["delivered_in_app"] == 1
    upd = riya.get("/v1/me/updates").json()[0]
    visible = str(upd["flats"]) + upd["text"]  # (ids are random, so check only what people read)
    assert len(upd["flats"]) == 2 and "1203" not in visible and "504" not in visible
