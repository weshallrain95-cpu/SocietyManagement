from datetime import date
from pathlib import Path

import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

from apps.identity.models import User
from apps.identity.tokens import issue_tokens
from apps.masterdata import dictionary
from apps.masterdata.models import Building, Locality, MicroMarket, Society, Unit
from apps.orgs.models import BrokerOrg, Membership
from common import rls

FIX = Path(__file__).parent / "fixtures"

# Real Thane West coordinates (approximate) used across tests.
DHOKALI = Point(72.9780, 19.2270, srid=4326)
MANPADA = Point(72.9700, 19.2330, srid=4326)
THANE_STN = Point(72.9750, 19.1860, srid=4326)


@pytest.fixture
def attrs(db):
    rows, version = dictionary.rows_from_yaml(FIX / "attributes_min.yaml")
    dictionary.load_rows(rows, version)


@pytest.fixture
def thane(db):
    mm = MicroMarket.objects.create(name="Thane West", launch_state="pilot")
    dh = Locality.objects.create(micro_market=mm, name="Dhokali", centroid=DHOKALI, pincodes=["400607"])
    mp = Locality.objects.create(micro_market=mm, name="Manpada", centroid=MANPADA, pincodes=["400610"])
    return {"mm": mm, "dhokali": dh, "manpada": mp}


@pytest.fixture
def society(thane):
    return Society.objects.create(canonical_name="Hiranandani Estate", locality=thane["dhokali"], location=DHOKALI, pincode="400607")


@pytest.fixture
def building(society):
    return Building.objects.create(society=society, name="Rodas A", location=society.location, floors_total=20)


@pytest.fixture
def unit(building, attrs):
    return Unit.objects.create(building=building, unit_no="1203", floor=12, bhk=2)


def make_user(phone, name=""):
    return User.objects.create_user(phone, display_name=name)


def make_org(name, phone, verified=True):
    user = make_user(phone, name)
    org = BrokerOrg.objects.create(
        name=name,
        txn_types=["RENT", "SALE_RESALE"],
        verification_status="verified" if verified else "pending",
        office_location=DHOKALI,
    )
    Membership.objects.create(user=user, org=org, role=Membership.Role.PRINCIPAL)
    return org, user


@pytest.fixture
def broker_a(db):
    return make_org("Suresh Realty", "9820000001")


@pytest.fixture
def broker_b(db):
    return make_org("Om Sai Estate Agents", "9820000002")


def api_for(user, org=None, role=None):
    c = APIClient()
    tokens = issue_tokens(user, org_id=org.pk if org else None, role=role or ("broker_principal" if org else "customer"))
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
    return c


@pytest.fixture
def as_org():
    """Context manager fixture: run ORM code as a broker org (RLS)."""
    return rls.org_context


@pytest.fixture
def platform():
    return rls.platform_context


TODAY = date(2026, 9, 23)


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


def agency_form(name, locality, **over):
    """A complete first-time registration (business form, founder decision 2026-09-25)."""
    return {
        "name": name,
        "legal_name": f"{name} (proprietor)",
        "ownership_type": "proprietorship",
        "owners": [{"name": f"{name} Owner"}],
        "pan": "ABCPS1234K",
        "gst_registered": False,
        "office_address": "Shop 3, Ground floor, Main Road",
        "office_locality": str(locality.pk),
        "office_pincode": "400607",
        "txn_types": ["RENT"],
        "service_locality_ids": [str(locality.pk)],
        "declaration": True,
        **over,
    }
