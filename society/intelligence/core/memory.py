from society.intelligence.persistence.models import IntelligenceMemoryEvent


class IntelligenceMemory:

    def __init__(self):
        self.local_events = []

    def record(self, event):
        self.local_events.append(event)

    def snapshot(self):
        # DB-backed snapshot = institutional memory
        total_events = IntelligenceMemoryEvent.objects.count()

        return {
            "events": total_events,
            "source": "persistent"
        }
