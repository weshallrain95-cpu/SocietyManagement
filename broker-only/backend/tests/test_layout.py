"""MD-10: building layouts; impossible flats and invented wings are caught at entry."""

import pytest

from apps.inventory import upload
from apps.inventory.models import UploadRow
from apps.masterdata.layout import check_flat, check_unit, expected_units
from apps.masterdata.models import Building, Unit
from common import rls
from common.models import ReviewQueueItem

from .conftest import api_for
from .test_upload import _xlsx

pytestmark = pytest.mark.django_db


@pytest.fixture
def rodas(society):
    """Hiranandani Estate with two verified wings: 20 floors from floor 1, 4 flats a floor, refuge floor 11, one penthouse."""
    kw = dict(society=society, location=society.location, floors_total=20, units_per_floor=4, skip_floors=[11], layout_verified=True)
    a = Building.objects.create(name="Rodas A", extra_unit_nos=["PH1"], **kw)
    b = Building.objects.create(name="Rodas B", **kw)
    society.wings_complete = True
    society.save()
    return a, b


def codes(issues):
    return [i.code for i in issues]


def test_valid_flats_pass(rodas):
    a, _ = rodas
    for no in ("101", "1204", "2004", "PH1", "ph-1"):
        assert check_unit(a, no) == [], no
    assert expected_units(a) == 19 * 4 + 1


@pytest.mark.parametrize(
    "no,floor,code",
    [
        ("2504", None, "above_top_floor"),
        ("1206", None, "no_such_flat_position"),
        ("1200", None, "no_such_flat_position"),
        ("1103", None, "no_flats_on_floor"),
        ("G01", None, "below_lowest_floor"),
        ("1203", 11, "floor_mismatch"),
    ],
)
def test_impossible_flats(rodas, no, floor, code):
    a, _ = rodas
    assert code in codes(check_unit(a, no, floor))


def test_verified_layout_blocks_unverified_only_warns(rodas):
    a, _ = rodas
    assert all(i.blocking for i in check_unit(a, "2504"))
    a.layout_verified = False
    assert not any(i.blocking for i in check_unit(a, "2504"))
    assert not any(i.blocking for i in check_unit(a, "1203", 11))  # a floor typo is never blocking


def test_unknown_layout_checks_nothing(society):
    b = Building.objects.create(society=society, name="Main", location=society.location)
    assert check_unit(b, "9999") == []


def test_wing_resolution(rodas, society):
    assert check_flat(society, "rodas-a", "1203")["building"]["name"] == "Rodas A"
    assert check_flat(society, None, "B-1203")["building"]["name"] == "Rodas B"  # wing in the flat number
    r = check_flat(society, None, "1203")
    assert codes(r["issues"]) == ["which_wing"] and r["blocking"] and r["suggestions"] == ["Rodas A", "Rodas B"]
    r = check_flat(society, "Rodaz C", "1203")
    assert codes(r["issues"]) == ["unknown_wing"] and r["blocking"] and r["building"] is None
    assert "Did you mean" in r["issues"][0].message


def test_open_society_warns_on_near_miss_and_allows_new_wing(society):
    Building.objects.create(society=society, name="Rodas A", location=society.location)
    r = check_flat(society, "Rodas B", "1203")
    assert codes(r["issues"]) == ["new_wing"] and not r["blocking"]
    assert check_flat(society, "Tower 7", "1203")["issues"] == []


def test_api_add_flat_blocks_warns_and_reports(rodas, society, broker_a):
    org, user = broker_a
    c = api_for(user, org)
    base = {"society_id": str(society.pk), "bhk": "2", "txn_type": "RENT", "asking_rent": 25000}

    r = c.get(f"/v1/societies/{society.pk}/check-flat", {"wing": "Rodas A", "unit_no": "2504"})
    assert r.status_code == 200 and r.json()["blocking"] and r.json()["issues"][0]["code"] == "above_top_floor"

    r = c.post("/v1/listings", base | {"building": "Rodas A", "unit_no": "2504"}, format="json")
    assert r.status_code == 422 and "20 floors" in r.json()["detail"]
    r = c.post("/v1/listings", base | {"building": "Rodas A", "unit_no": "2504", "confirm_layout": True}, format="json")
    assert r.status_code == 422  # a verified layout cannot be overridden by a broker
    r = c.post("/v1/listings", base | {"unit_no": "1203"}, format="json")
    assert r.status_code == 422 and r.json()["layout"]["suggestions"] == ["Rodas A", "Rodas B"]

    a, _ = rodas
    a.layout_verified = False
    a.save()
    r = c.post("/v1/listings", base | {"building": "Rodas A", "unit_no": "2504"}, format="json")
    assert r.status_code == 409
    r = c.post("/v1/listings", base | {"building": "Rodas A", "unit_no": "2504", "confirm_layout": True}, format="json")
    assert r.status_code == 201

    r = c.post(f"/v1/buildings/{a.pk}/layout-report", {"unit_no": "2601", "note": "new floor added"}, format="json")
    assert r.status_code == 202
    assert ReviewQueueItem.objects.filter(kind="layout_report", data__unit_no="2601").exists()


def test_upload_rejects_impossible_rows(rodas, society, attrs, thane, broker_a):
    org, user = broker_a
    sheet = [
        ["Society", "Wing", "Flat", "BHK", "Rent"],
        ["Hiranandani Estate", "Rodas A", "1203", "2", "25000"],
        ["Hiranandani Estate", "Rodas A", "2504", "2", "25000"],
        ["Hiranandani Estate", "Rodas Z", "1203", "2", "25000"],
    ]
    with rls.org_context(org.pk):
        batch = upload.create_batch(org=org, user=user, filename="f.xlsx", content=_xlsx(sheet), micro_market=thane["mm"])
        assert upload.commit_batch(batch, user=user)["committed"] == 1
        rows = {r.parsed["unit_no"] + r.parsed["wing"]: r for r in batch.rows.all()}
        assert rows["1203Rodas A"].resolution == UploadRow.Resolution.COMMITTED
        assert rows["2504Rodas A"].resolution == UploadRow.Resolution.ERROR and "20 floors" in rows["2504Rodas A"].errors[0]
        assert rows["1203Rodas Z"].resolution == UploadRow.Resolution.ERROR and "no wing" in rows["1203Rodas Z"].errors[0]
    assert not Unit.objects.filter(unit_no="2504").exists()
    assert not Building.objects.filter(name="Rodas Z").exists()


def test_import_building_layouts(tmp_path, society, thane):
    from django.core.management import call_command

    from apps.masterdata.models import Society

    sheet = [
        ["Society", "Wing", "Floors", "First floor with flats", "Flats per floor", "Floors with no flats", "Source", "Verified"],
        ["Example – Hiranandani Estate", "Rodas A", 20, 1, 4, "11", "survey", "yes"],
        ["Hiranandani Estate", "Rodas A", 20, 1, 4, "11", "survey", "yes"],
        ["Hiranandani Estate", "Rodas B", 18, 0, 6, "", "rera", "no"],
        ["Nowhere Towers", "A", 10, 1, 4, "", "", ""],
        ["Hiranandani Estate", "Rodas C", "twenty", 1, 4, "", "", ""],
    ]
    f = tmp_path / "layouts.xlsx"
    f.write_bytes(_xlsx(sheet))
    call_command("import_building_layouts", str(f), "--dry-run")
    assert not Building.objects.filter(society=society).exists()

    call_command("import_building_layouts", str(f), "--mark-complete")
    a = Building.objects.get(society=society, name="Rodas A")
    b = Building.objects.get(society=society, name="Rodas B")
    assert (a.floors_total, a.units_per_floor, a.skip_floors, a.layout_verified) == (20, 4, [11], True)
    assert (b.lowest_floor, b.units_per_floor, b.layout_verified, b.layout_source) == (0, 6, False, "rera")
    assert not Building.objects.filter(name="Rodas C").exists()  # bad row skipped, reported
    assert Society.objects.get(pk=society.pk).wings_complete
    assert check_flat(society, "Rodas A", "2104")["blocking"]


def test_ops_edits_layout_and_wings(society):
    from django.test import Client

    from .conftest import make_user

    u = make_user("9000000019", "Ops")
    u.is_staff = True
    u.save()
    c = Client()
    c.force_login(u)
    url = f"/ops/societies/{society.pk}"
    c.post(url, {"action": "add_wing", "wing": "Rodas A"})
    b = Building.objects.get(society=society, name="Rodas A")
    form = {"action": "layout", "building_id": str(b.pk), "floors_total": "20", "lowest_floor": "1", "units_per_floor": "4"}
    r = c.post(url, form | {"skip_floors": "11, 22x", "layout_verified": "1"}, follow=True)
    assert "must be numbers" in r.content.decode()
    c.post(url, form | {"skip_floors": "11", "layout_source": "survey", "layout_verified": "1"})
    b.refresh_from_db()
    assert (b.floors_total, b.skip_floors, b.layout_verified, b.layout_source) == (20, [11], True, "survey")
    c.post(url, {"action": "wings_complete", "value": "1"})
    society.refresh_from_db()
    assert society.wings_complete
    page = c.get(url).content.decode()
    assert "0 of 76" in page and "All wings on record" in page
