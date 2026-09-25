"""MahaRERA public project list -> societies (D18): link known societies, propose the rest to ops."""

import csv

import pytest

from apps.masterdata.models import Society
from apps.masterdata.rera import complex_name, import_projects, read_projects
from common.models import ReviewQueueItem

pytestmark = pytest.mark.django_db

ROWS = [
    ("P51700000011", "HIRANANDANI ESTATE - RODAS ENCLAVE - B", "400607"),
    ("P51700000012", "LODHA SPLENDORA - PLATINO - B", "400615"),
    ("P51700000013", "LODHA SPLENDORA - PLATINO - D", "400615"),
    ("P51700000014", "TOKYO BAY PHASE 2A", "400607"),
    ("P51700000015", "GRAND HOTEL", "400607"),  # not housing
    ("P51700000016", "SUNRISE TOWERS", "421301"),  # outside the pilot pin codes
]


@pytest.fixture
def rera_csv(tmp_path):
    p = tmp_path / "projects.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "rera_no",
                "project_name",
                "promoter",
                "location",
                "pincode",
                "district",
                "state",
                "lat",
                "lng",
                "last_modified",
                "details_url",
            ]
        )
        for no, name, pin in ROWS:
            w.writerow([no, name, "Promoter Pvt Ltd", "Thane", pin, "Thane", "MAHARASHTRA", "", "", "2025-01-01", f"https://example/{no}"])
    return str(p)


def test_complex_name_splits_building_and_phase():
    assert complex_name("LODHA SPLENDORA - PLATINO - B") == ("LODHA SPLENDORA", "PLATINO - B")
    assert complex_name("TOKYO BAY PHASE 2A") == ("TOKYO BAY", "PHASE 2A")
    assert complex_name("REDEVELOPMENT OF PARIJAT CHS")[0] == "PARIJAT CHS"


def test_import_links_known_societies_and_proposes_the_rest(society, rera_csv):
    groups = read_projects(rera_csv)
    assert {g.name for g in groups.values()} == {"Hiranandani Estate", "Lodha Splendora", "Tokyo Bay"}

    res = import_projects(groups)
    society.refresh_from_db()
    assert society.rera_project_nos == ["P51700000011"]  # known society: RERA number added, nothing renamed
    assert "RODAS ENCLAVE - B" in society.provenance["rera_buildings"]

    splendora = Society.objects.get(canonical_name="Lodha Splendora")
    assert splendora.status == Society.Status.PROVISIONAL and splendora.kind == Society.Kind.PROJECT
    assert splendora.rera_project_nos == ["P51700000012", "P51700000013"]  # two phases, one society
    assert splendora.provenance["location_approx"] is True
    assert ReviewQueueItem.objects.filter(kind="provisional_society", ref_id=str(splendora.pk)).exists()
    assert len(res.proposed) == 2 and len(res.matched) == 1

    again = import_projects(read_projects(rera_csv))  # re-running changes nothing
    assert again.already == 3 and not again.proposed
    assert Society.objects.filter(canonical_name="Lodha Splendora").count() == 1


def test_dry_run_saves_nothing(society, rera_csv):
    before = Society.objects.count()
    import_projects(read_projects(rera_csv), dry_run=True)
    society.refresh_from_db()
    assert Society.objects.count() == before and society.rera_project_nos == []
