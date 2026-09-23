import pytest

from apps.masterdata.normalise import normalise_building, normalise_name, normalise_unit_no


@pytest.mark.parametrize(
    "raw,expected_text",
    [
        ("Hiranandani Estate", "hiranandani estate"),
        ("HIRANANDANI ESTATE CHS LTD, Thane", "hiranandani estate chs"),
        ("Hira Nandani Est.", "hira nandani estate"),
        ("Shree Ganesh Co-op Hsg Soc Ltd", "shree ganesh chs"),
        ("Kalpataru Srishti Apts", "kalpataru srishti apartment"),
        ("Rodas Encl., Ghodbunder Rd", "rodas enclave"),
    ],
)
def test_normalise_name(raw, expected_text):
    assert normalise_name(raw).text == expected_text


def test_locality_and_wing_hints_are_extracted():
    n = normalise_name("Lodha Amara Tower 12, Kolshet")
    assert n.text == "lodha amara"
    assert n.building_hint == "12"
    assert n.locality_hint == "kolshet"


def test_split_brand_words_share_a_skeleton():
    assert normalise_name("Hira Nandani Est.").skeleton == normalise_name("Hiranandani Estate").skeleton


def test_devanagari_is_transliterated():
    n = normalise_name("हिरानंदानी इस्टेट")
    assert "estate" in n.tokens
    assert n.skeleton.startswith("hiran")


def test_locality_alone_is_kept_as_name():
    assert normalise_name("Vasant Vihar").text == "vasant vihar"


@pytest.mark.parametrize(
    "raw,unit_no,floor,wing",
    [
        ("B-1203", "1203", 12, "B"),
        ("1203", "1203", 12, ""),
        ("12/03", "1203", 12, ""),
        ("Flat 1203, 12th flr", "1203", 12, ""),
        ("G-2", "G2", 0, ""),
        ("A 504", "504", 5, "A"),
        ("b1102", "1102", 11, "B"),
        ("Flat No. 7", "7", None, ""),
    ],
)
def test_unit_numbers(raw, unit_no, floor, wing):
    u = normalise_unit_no(raw)
    assert (u.unit_no, u.floor, u.wing) == (unit_no, floor, wing)


def test_building_names():
    assert normalise_building("A Wing") == normalise_building("Wing A") == "A"
    assert normalise_building("Tower 3") == "3"
    assert normalise_building("") == "MAIN"
