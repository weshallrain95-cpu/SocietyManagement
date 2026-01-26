from .models import IntelligenceMemoryEvent


class IntelligenceMemoryRepository:

    @staticmethod
    def store(event_type, node_id, workflow_id, payload, scores=None):
        return IntelligenceMemoryEvent.objects.create(
            event_type=event_type,
            node_id=node_id,
            workflow_id=workflow_id,
            payload=payload,
            risk_score=(scores or {}).get("risk"),
            confidence_score=(scores or {}).get("confidence"),
        )

    @staticmethod
    def fetch_by_node(node_id):
        return IntelligenceMemoryEvent.objects.filter(node_id=node_id).order_by("-timestamp")

    @staticmethod
    def fetch_by_workflow(workflow_id):
        return IntelligenceMemoryEvent.objects.filter(workflow_id=workflow_id).order_by("-timestamp")
