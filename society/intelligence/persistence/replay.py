from .models import IntelligenceMemoryEvent


class IntelligenceReplayEngine:

    @staticmethod
    def replay_workflow(workflow_id):
        return IntelligenceMemoryEvent.objects.filter(
            workflow_id=workflow_id
        ).order_by("timestamp")
