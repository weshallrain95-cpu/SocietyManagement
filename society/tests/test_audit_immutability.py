import pytest
from django.core.exceptions import ValidationError
from society.domain_services.audit import create_audit_event, compute_event_hash

from society.models import ChartOfAccount, Society
import pytest

@pytest.fixture
def account(db):
    society = Society.objects.first()
    if not society:
        society = Society.objects.create(name="Test Society")

    return ChartOfAccount.objects.create(
        society=society,
        code="TEST_ACC",
        name="Test Account",
        account_type="ASSET"
    )

@pytest.mark.django_db
def test_audit_event_cannot_be_updated():
    event = create_audit_event(
        actor=None,
        actor_role="SYSTEM",
        event_type="TEST",
        object_type="X",
        object_id="1",
        action="CREATE",
        payload={}
    )

    event.action = "HACK"
    with pytest.raises(ValidationError):
        event.save()
def test_pytest_is_working():
    assert True
@pytest.mark.django_db
def test_audit_event_cannot_be_deleted():
    event = create_audit_event(
        actor=None,
        actor_role="SYSTEM",
        event_type="TEST",
        object_type="X",
        object_id="2",
        action="CREATE",
        payload={}
    )

    with pytest.raises(Exception):
        event.delete()
@pytest.mark.django_db
def test_audit_hash_chain_integrity():
    e1 = create_audit_event(
        actor=None,
        actor_role="SYSTEM",
        event_type="TEST",
        object_type="X",
        object_id="1",
        action="CREATE",
        payload={}
    )

    e2 = create_audit_event(
        actor=None,
        actor_role="SYSTEM",
        event_type="TEST",
        object_type="X",
        object_id="2",
        action="CREATE",
        payload={}
    )

    assert e2.previous_hash == e1.event_hash
from society.models import AuditEvent
from society.domain_services.audit import compute_event_hash


def verify_chain():
    events = AuditEvent.objects.order_by("created_at")
    prev = ""
    for e in events:
        expected = compute_event_hash(e, prev)
        if expected != e.event_hash:
            return False
        prev = e.event_hash
    return True

@pytest.mark.django_db
def test_audit_chain_detects_tampering():
    e = create_audit_event(
        actor=None,
        actor_role="SYSTEM",
        event_type="TEST",
        object_type="X",
        object_id="3",
        action="CREATE",
        payload={}
    )

    AuditEvent.objects.filter(pk=e.pk).update(event_type="TAMPERED")
    assert verify_chain() is False
import pytest
from society.models import LedgerEntry

@pytest.mark.django_db
def test_ledger_entry_requires_audit_event(account):
    with pytest.raises(Exception):
        LedgerEntry.objects.create(
            account=account,
            amount=100
        )
