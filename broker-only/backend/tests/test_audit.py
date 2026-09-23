import pytest
from django.db import DatabaseError, transaction

from apps.audit.models import AuditEvent
from apps.audit.services import audit, verify_chain

pytestmark = pytest.mark.django_db


def test_chain_verifies_and_detects_nothing_when_clean(broker_a):
    org, user = broker_a
    for i in range(5):
        audit(user, "test.event", org, {"i": i, "nested": {"b": 2, "a": 1}})
    assert verify_chain() == {"ok": True, "checked": 5, "head": AuditEvent.objects.order_by("-seq").first().hash}


def test_audit_rows_cannot_be_edited_or_deleted(broker_a):
    org, user = broker_a
    ev = audit(user, "test.event", org)
    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.filter(pk=ev.pk).update(action="tampered")
    with pytest.raises(DatabaseError), transaction.atomic():
        AuditEvent.objects.filter(pk=ev.pk).delete()
