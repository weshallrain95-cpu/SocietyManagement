"""NFR-04: one broker's inventory must never be readable or writable by another."""

import pytest
from django.db import DataError, ProgrammingError, connection
from django.utils import timezone

from apps.crm.models import Customer
from apps.inventory.models import Listing
from common import crypto, rls

pytestmark = pytest.mark.django_db


def _listing(org, unit):
    return Listing.objects.create(org=org, unit=unit, txn_type="RENT", asking_rent=25000, last_confirmed_at=timezone.now())


def test_app_role_is_not_superuser():
    with connection.cursor() as cur:
        cur.execute("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
        assert cur.fetchone() == (False, False), "RLS is silently bypassed for superusers"


def test_listings_are_isolated(unit, broker_a, broker_b):
    org_a, org_b = broker_a[0], broker_b[0]
    with rls.org_context(org_a.pk):
        la = _listing(org_a, unit)
    with rls.org_context(org_b.pk):
        _listing(org_b, unit)
        assert list(Listing.objects.values_list("org_id", flat=True)) == [org_b.pk]
        assert not Listing.objects.filter(pk=la.pk).exists()
        # Even a raw SQL read cannot see another org's row.
        with connection.cursor() as cur:
            cur.execute("SELECT count(*) FROM inventory_listing")
            assert cur.fetchone()[0] == 1
        assert Listing.objects.filter(pk=la.pk).update(asking_rent=1) == 0


def test_no_context_sees_nothing(unit, broker_a):
    org_a = broker_a[0]
    with rls.org_context(org_a.pk):
        _listing(org_a, unit)
    rls.clear()
    assert Listing.objects.count() == 0


def test_cannot_insert_for_another_org(unit, broker_a, broker_b):
    with rls.org_context(broker_a[0].pk):
        with pytest.raises(ProgrammingError):
            from django.db import transaction

            with transaction.atomic():
                _listing(broker_b[0], unit)


def test_platform_context_sees_all(unit, broker_a, broker_b):
    for org, _ in (broker_a, broker_b):
        with rls.org_context(org.pk):
            _listing(org, unit)
    with rls.platform_context():
        assert Listing.objects.count() == 2


def test_customer_books_are_isolated(broker_a, broker_b):
    phone = "+919876500000"
    for org, _ in (broker_a, broker_b):
        with rls.org_context(org.pk):
            Customer.objects.create(org=org, phone_hash=crypto.phone_hash(phone), phone_enc=crypto.encrypt(phone), source="walk_in")
    with rls.org_context(broker_a[0].pk):
        assert Customer.objects.count() == 1


def test_every_broker_private_table_has_forced_rls():
    private = {
        "inventory_listing",
        "inventory_keycustody",
        "inventory_uploadbatch",
        "inventory_uploadrow",
        "inventory_savedcolumnmapping",
        "crm_customer",
        "crm_requirement",
        "crm_customerinteraction",
        "crm_shortlist",
        "crm_shortlistitem",
        "matching_matchrun",
        "matching_matchresult",
        "visits_visitplan",
        "visits_visitstop",
        "visits_syncmutation",
    }
    with connection.cursor() as cur:
        cur.execute("SELECT relname FROM pg_class WHERE relrowsecurity AND relforcerowsecurity")
        forced = {r[0] for r in cur.fetchall()}
        cur.execute("SELECT table_name FROM information_schema.columns WHERE column_name = 'broker_org_id' AND table_schema = 'public'")
        with_org_column = {r[0] for r in cur.fetchall()}
    assert private <= forced
    assert with_org_column <= forced, f"tables with broker_org_id but no RLS: {with_org_column - forced}"


def test_bad_org_setting_is_rejected():
    with pytest.raises(DataError):
        from django.db import transaction

        with transaction.atomic():
            rls.set_org("not-a-uuid")
            Listing.objects.count()
