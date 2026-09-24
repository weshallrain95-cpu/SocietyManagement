"""D18: wings, floors and flats come from official lists (TMC property-tax register, MahaRERA, IGR), never
from brokers. The layout is worked out from the list; flats outside a complete list cannot be added; the
building can be shown floor by floor with the broker's own flats marked (and nobody else's)."""

import pytest
from django.core.management import call_command

from apps.inventory.services import create_listing
from apps.masterdata.models import Building, RegisterFlat, Unit
from apps.masterdata.registers import derive_layout, import_register
from common import rls

from .conftest import api_for

pytestmark = pytest.mark.django_db


def _register_csv():
    """Rodas A as TMC lists it: floors 1–14, 4 flats a floor, floor 7 is a refuge floor, penthouse 1405A.
    The owner column is there, as in the real extract; it must never be stored."""
    lines = ["Society,Wing,Flat No,Floor,Carpet Area,Property No,Prabhag Samiti,Owner Name"]
    for fl in range(1, 15):
        if fl == 7:
            continue
        for p in range(1, 5):
            lines.append(f"Hiranandani Estate,Rodas A,{fl}{p:02d},{fl},650,MJ{fl:02d}{p:02d}17,Majiwada,Some Owner {fl}{p}")
    lines.append("Hiranandani Estate,Rodas A,1405A,14,1400,MJ140517,Majiwada,Penthouse Owner")
    return "\n".join(lines).encode()


def test_derive_layout_from_a_full_list():
    flats = [(f"{fl}{p:02d}", fl) for fl in range(1, 21) if fl not in (7, 14) for p in range(1, 7)] + [("2001A", 20), ("G01", 0)]
    d = derive_layout(flats)
    assert (d.floors_total, d.lowest_floor, d.units_per_floor) == (20, 0, 6)
    assert d.skip_floors == [7, 14] and d.extra_unit_nos == ["2001A", "G01"]


def test_import_tmc_register_sets_verified_layout_and_drops_owner_names(society):
    res = import_register("tmc-majiwada.csv", _register_csv(), source="tmc")
    assert (res.wings, res.flats_new) == (1, 53)
    assert "Owner Name" in res.ignored_columns
    b = Building.objects.get(society=society, name="Rodas A")
    assert (b.floors_total, b.lowest_floor, b.units_per_floor, b.skip_floors, b.extra_unit_nos) == (14, 1, 4, [7], ["1405A"])
    assert b.layout_source == "tmc" and b.layout_verified and b.register_complete
    f = RegisterFlat.objects.get(building=b, unit_no_normalised="1203")
    assert (f.floor, f.source_ref, f.ward, int(f.carpet_sqft)) == (12, "MJ120317", "Majiwada", 650)
    assert "Owner" not in str(list(RegisterFlat.objects.values()))
    # Re-importing is harmless.
    again = import_register("tmc-majiwada.csv", _register_csv(), source="tmc")
    assert (again.flats_new, again.flats_known) == (0, 53)


def test_command_and_dry_run(society, tmp_path, capsys):
    p = tmp_path / "rodas.csv"
    p.write_bytes(_register_csv())
    call_command("import_flat_register", str(p), "--source", "tmc", "--dry-run")
    assert not RegisterFlat.objects.exists()
    call_command("import_flat_register", str(p), "--source", "tmc")
    out = capsys.readouterr().out
    assert "Rodas A: floors 1–14, 4 per floor, no flats on [7], extra ['1405A'] (53 flats)" in out
    assert "ignored columns (never stored): Owner Name" in out


def test_complete_register_is_the_last_word_on_flat_numbers(society, broker_a):
    import_register("tmc.csv", _register_csv(), source="tmc")
    org, user = broker_a
    c = api_for(user, org)
    ok = c.get(f"/v1/societies/{society.pk}/check-flat", {"wing": "Rodas A", "unit_no": "1405A"}).json()
    assert ok["issues"] == []
    bad = c.get(f"/v1/societies/{society.pk}/check-flat", {"wing": "Rodas A", "unit_no": "705"}).json()
    assert bad["blocking"] and bad["issues"][0]["message"] == "Flat 705 is not in the TMC property tax list of flats in Rodas A."


def test_structure_picture_marks_only_my_flats(society, attrs, broker_a, broker_b):
    import_register("tmc.csv", _register_csv(), source="tmc")
    b = Building.objects.get(name="Rodas A")
    org, user = broker_a
    borg, buser = broker_b
    with rls.org_context(org.pk):
        create_listing(
            org=org, user=user, unit=Unit.objects.create(building=b, unit_no="1203", bhk=2), txn_type="RENT", data={"asking_rent": 24000}
        )
    with rls.org_context(borg.pk):
        create_listing(
            org=borg, user=buser, unit=Unit.objects.create(building=b, unit_no="302", bhk=2), txn_type="RENT", data={"asking_rent": 22000}
        )
    s = api_for(user, org).get(f"/v1/societies/{society.pk}/structure").json()
    wing = s["wings"][0]
    assert s["sources"] == ["tmc"] and wing["flats_total"] == 53
    assert [r["label"] for r in wing["floors"]][:3] == ["14", "13", "12"]
    assert next(r for r in wing["floors"] if r["floor"] == 7)["no_flats"]
    assert [f["no"] for f in wing["floors"][0]["flats"]] == ["1401", "1402", "1403", "1404", "1405A"]
    mine = [f["no"] for r in wing["floors"] for f in r["flats"] if f["mine"]]
    assert mine == ["1203"]  # broker B's 302 is never revealed
