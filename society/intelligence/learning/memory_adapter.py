from society.intelligence.persistence.repository import IntelligenceMemoryRepository
from datetime import datetime


class LearningMemoryAdapter:
    """
    Adapter between LearningEngine and IntelligenceMemoryRepository
    """

    def store(self, event: dict):
        scores = event.get("scores", {})
        IntelligenceMemoryRepository.store(
            event_type=event.get("event_type", "unknown"),
            node_id=event.get("node_id"),
            workflow_id=event.get("workflow_id"),
            payload=event.get("payload", {}),
            scores={
                "risk": scores.get("risk", 0.0),
                "confidence": scores.get("confidence", 0.0)
            }
        )

    def fetch_all(self):
        from society.models import IntelligenceMemoryEvent
        return list(IntelligenceMemoryEvent.objects.all().values())
