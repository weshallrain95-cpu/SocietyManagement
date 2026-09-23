import pytest
from django.utils import timezone

from apps.masterdata.models import OwnershipClaim
from apps.status import services as st
from apps.status.models import State, StatusConfirmation, StatusEvent
from common.links import LinkError, resolve_link

from .conftest import make_user

pytestmark = pytest.mark.django_db
B = st.Actor.broker


@pytest.fixture
def owner(unit):
    u = make_user("9819000001", "Mrs Kulkarni")
    OwnershipClaim.objects.create(unit=unit, user=u, status="verified", verified_at=timezone.now())
    return u


def test_broker_listing_without_owner_is_unconfirmed(unit, broker_a):
    s = st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    assert s.state == State.AVAILABLE_UNCONFIRMED
    assert s.label == "Available for rent – not yet confirmed by owner"


def test_two_independent_brokers_make_consensus(unit, broker_a, broker_b):
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))  # same broker twice is still one voice
    assert st.get_status(unit, "RENT").state == State.AVAILABLE_UNCONFIRMED
    s = st.report(unit, "RENT", "AVAILABLE", B(broker_b[0]))
    assert s.state == State.AVAILABLE and s.source_type == "consensus"


def test_downgrade_is_immediate(unit, broker_a, broker_b):
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    s = st.report(unit, "RENT", "LET", B(broker_b[0]))
    assert s.state == State.LET


def test_reopening_a_let_unit_needs_the_owner(unit, broker_a, owner):
    st.report(unit, "RENT", "LET", B(broker_a[0]))
    s = st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    assert s.state == State.AVAILABLE_UNCONFIRMED
    conf = StatusConfirmation.objects.get(unit=unit)
    assert conf.previous_state == State.LET and conf.owner == owner
    # Owner says YES via the link.
    s = st.owner_responds(conf, "yes")
    assert s.state == State.AVAILABLE and s.confirmed_by_owner


def test_owner_no_reverts_and_penalises_broker(unit, broker_a, owner):
    org = broker_a[0]
    st.report(unit, "RENT", "LET", B(org))
    st.report(unit, "RENT", "AVAILABLE", B(org))
    conf = StatusConfirmation.objects.get(unit=unit)
    s = st.owner_responds(conf, "no")
    assert s.state == State.LET
    org.refresh_from_db()
    assert float(org.listing_accuracy) < 1


def test_broker_consensus_does_not_override_a_verified_owner(unit, broker_a, broker_b, owner):
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    s = st.report(unit, "RENT", "AVAILABLE", B(broker_b[0]))
    assert s.state == State.AVAILABLE_UNCONFIRMED
    assert StatusConfirmation.objects.filter(unit=unit, response="").count() == 1  # not spammed twice


def test_hold_released_by_same_broker(unit, broker_a, broker_b):
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    st.report(unit, "RENT", "AVAILABLE", B(broker_b[0]))
    st.report(unit, "RENT", "ON_HOLD", B(broker_a[0]))
    # Another broker cannot release A's hold...
    assert st.report(unit, "RENT", "AVAILABLE", B(broker_b[0])).state == State.ON_HOLD
    # ...but A can.
    assert st.report(unit, "RENT", "AVAILABLE", B(broker_a[0])).state == State.AVAILABLE


def test_let_is_rent_only(unit, broker_a):
    with pytest.raises(st.StatusError):
        st.report(unit, "SALE_RESALE", "LET", B(broker_a[0]))


def test_confirmation_link_is_single_use(unit, broker_a, owner):
    st.report(unit, "RENT", "LET", B(broker_a[0]))
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    conf = StatusConfirmation.objects.get(unit=unit)
    # Tokens are never stored: find it through a fresh request.
    conf.link.delete()
    conf.refresh_from_db()
    conf2 = st.request_owner_confirmation(unit, "RENT", previous_state=State.LET, org=broker_a[0], owner=owner)
    token = conf2._token
    resolve_link(token, "status_confirmation", consume=True)
    with pytest.raises(LinkError):
        resolve_link(token, "status_confirmation", consume=True)


def test_ledger_is_hash_chained_and_append_only(unit, broker_a, broker_b):
    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    st.report(unit, "RENT", "AVAILABLE", B(broker_b[0]))
    st.report(unit, "RENT", "LET", B(broker_a[0]))
    assert StatusEvent.objects.count() == 3
    assert st.verify_ledger()["ok"]
    from django.db import DatabaseError, transaction

    with pytest.raises(DatabaseError), transaction.atomic():
        StatusEvent.objects.filter(seq=StatusEvent.objects.first().seq).update(to_state="SOLD")


def test_decay(unit, broker_a, broker_b):
    from datetime import timedelta

    st.report(unit, "RENT", "AVAILABLE", B(broker_a[0]))
    st.report(unit, "RENT", "AVAILABLE", B(broker_b[0]))
    assert st.decay_stale(now=timezone.now() + timedelta(days=31)) == 1
    assert st.get_status(unit, "RENT").state == State.AVAILABLE_UNCONFIRMED


def test_hold_expires(unit, broker_a):
    from datetime import timedelta

    st.report(unit, "RENT", "ON_HOLD", B(broker_a[0]))
    assert st.decay_stale(now=timezone.now() + timedelta(days=8)) == 1
    assert st.get_status(unit, "RENT").state == State.AVAILABLE_UNCONFIRMED
