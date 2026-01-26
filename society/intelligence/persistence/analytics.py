from .models import IntelligenceMemoryEvent


class IntelligenceAnalytics:

    @staticmethod
    def failure_rates():
        total = IntelligenceMemoryEvent.objects.count()
        failures = IntelligenceMemoryEvent.objects.filter(event_type="failure").count()
        if total == 0:
            return 0
        return failures / total

    @staticmethod
    def node_failure_map():
        data = {}
        for e in IntelligenceMemoryEvent.objects.filter(event_type="failure"):
            data.setdefault(e.node_id, 0)
            data[e.node_id] += 1
        return data
