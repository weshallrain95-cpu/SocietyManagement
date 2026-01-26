import pytest
from society.intelligence.persistence.repository import IntelligenceMemoryRepository
from society.intelligence.persistence.models import IntelligenceMemoryEvent


@pytest.mark.django_db
def test_memory_persistence_store():
    IntelligenceMemoryRepository.store(
        event_type="success",
        node_id="N1",
        workflow_id="WF1",
        payload={"ok": True},
        scores={"risk": 0.2, "confidence": 0.9}
    )

    assert IntelligenceMemoryEvent.objects.count() == 1


@pytest.mark.django_db
def test_memory_fetch_by_node():
    IntelligenceMemoryRepository.store(
        event_type="failure",
        node_id="N2",
        workflow_id="WF1",
        payload={"error": "x"},
        scores={"risk": 0.8, "confidence": 0.1}
    )

    events = IntelligenceMemoryRepository.fetch_by_node("N2")
    assert events.count() == 1
