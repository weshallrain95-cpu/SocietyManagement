import io

import pytest
from openpyxl import Workbook

from apps.inventory import upload
from apps.inventory.models import Listing, UploadRow
from apps.masterdata.models import Society, Unit
from common import rls

from .conftest import DHOKALI

pytestmark = pytest.mark.django_db

# A realistic, messy broker sheet: their own headers, spellings, formats.
SHEET = [
    ["Bldg Name", "Wing", "Flat No", "Config", "Rent", "Dep", "Avail", "Owner", "Owner Mobile", "Pets", "Remarks"],
    ["Hiranandani Estate", "Rodas A", "1203", "2 BHK", "25,000", "75k", "01/11/2026", "Kulkarni", "98190 00001", "yes", "good view"],
    ["HIRANANDANI ESTATE CHS LTD", "Rodas A", "1204", "2bhk", "24000", "1.5 lakh", "now", "Shah", "9819000002", "", ""],
    ["Hira Nandani Est.", "Rodas B", "B-502", "1 RK", "12k", "", "", "", "", "no", ""],
    ["Shanti Niwas", "", "7", "1BHK", "15000", "", "", "", "", "", ""],
    ["Sai Krupa Residency", "", "301", "2", "18000", "", "", "", "", "", ""],
    ["Hiranandani Estate", "", "", "2BHK", "20000", "", "", "", "", "", "missing flat"],
    ["Hiranandani Estate", "Rodas A", "1205", "two", "=HYPERLINK(\"x\")", "", "", "", "", "", ""],
]


def _xlsx(rows):
    wb = Workbook()
    for r in rows:
        wb.active.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


@pytest.fixture
def shanti_twice(thane):
    for loc in ("dhokali", "manpada"):
        Society.objects.create(canonical_name="Shanti Niwas", locality=thane[loc], location=thane[loc].centroid)


def test_messy_sheet_end_to_end(society, attrs, thane, broker_a, shanti_twice):
    org, user = broker_a
    with rls.org_context(org.pk):
        batch = upload.create_batch(org=org, user=user, filename="my flats.xlsx", content=_xlsx(SHEET), micro_market=thane["mm"])
        rows = {r.row_no: r for r in batch.rows.all()}
        assert batch.column_mapping["Bldg Name"] == "society" and batch.column_mapping["Dep"] == "deposit"
        assert [rows[i].resolution for i in (2, 3, 4)] == ["auto", "auto", "auto"]
        assert rows[5].resolution == "needs_confirmation"  # same name in two localities
        assert rows[6].resolution == "provisional"  # unknown society
        assert rows[7].resolution == "error" and "Flat number is missing" in rows[7].errors
        assert rows[8].resolution == "error"
        assert rows[3].parsed["deposit"] == 150000 and rows[4].parsed["bhk"] == 0.5

        # Broker resolves the ambiguous row and proposes the unknown society.
        choice = rows[5].candidates[0]["society_id"]
        upload.resolve_row(rows[5], user=user, society_id=choice)
        upload.resolve_row(rows[6], user=user, propose={"locality_id": thane["dhokali"].pk, "lat": DHOKALI.y, "lng": DHOKALI.x})
        result = upload.commit_batch(batch, user=user)
        assert result["committed"] == 5, {r.row_no: (r.resolution, r.errors, r.society_id is not None) for r in batch.rows.all()}
        assert Listing.objects.count() == 5
        l1203 = Listing.objects.get(unit__unit_no="1203")
        assert l1203.deposit == 75000 and l1203.owner_phone == "+919819000001"
    # 1203 and 1204 landed in ONE society/building, not three.
    assert Unit.objects.filter(building__society=society).count() == 3
    assert Society.objects.filter(canonical_name__icontains="nandani").count() == 1
    assert Society.objects.get(canonical_name="Sai Krupa Residency").status == "provisional"


def test_mapping_is_remembered(society, attrs, thane, broker_a):
    org, user = broker_a
    custom = {"Bldg Name": "society", "Wing": "wing", "Flat No": "unit_no", "Config": "bhk", "Rent": "asking_rent"}
    with rls.org_context(org.pk):
        upload.create_batch(org=org, user=user, filename="a.xlsx", content=_xlsx(SHEET[:2]), micro_market=thane["mm"], mapping=custom)
        again = upload.create_batch(org=org, user=user, filename="b.xlsx", content=_xlsx(SHEET[:2]), micro_market=thane["mm"])
        assert again.column_mapping == custom


def test_csv_upload(society, attrs, thane, broker_a):
    org, user = broker_a
    csv_bytes = "Society,Flat,BHK,Rent\nHiranandani Estate,1601,3,45000\n".encode()
    with rls.org_context(org.pk):
        batch = upload.create_batch(org=org, user=user, filename="x.csv", content=csv_bytes, micro_market=thane["mm"])
        assert batch.rows.get().resolution == UploadRow.Resolution.AUTO
        assert upload.commit_batch(batch, user=user)["committed"] == 1


def test_other_broker_cannot_see_batch(society, attrs, thane, broker_a, broker_b):
    org, user = broker_a
    with rls.org_context(org.pk):
        batch = upload.create_batch(org=org, user=user, filename="x.csv", content=b"Society,Flat,BHK\nHiranandani Estate,1,2\n", micro_market=thane["mm"])
    with rls.org_context(broker_b[0].pk):
        assert not UploadRow.objects.filter(batch_id=batch.pk).exists()
