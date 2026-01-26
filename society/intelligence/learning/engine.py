from datetime import datetime
from .memory_adapter import LearningMemoryAdapter


class LearningEngine:
    """
    Core system learning engine.
    This is NOT ML, not AI models — it's institutional learning logic:
    memory, reinforcement, adaptation, evolution substrate.
    """

    def __init__(self, memory_repo=None):
        # Persistent learning memory
        self.memory = memory_repo or LearningMemoryAdapter()

    def observe(self, context, event: dict):
        """
        Observe any system event and persist learning signal
        """
        normalized = {
            "event_type": event.get("event_type", "unknown"),
            "node_id": event.get("node_id"),
            "workflow_id": event.get("workflow_id"),
            "payload": event.get("payload", {}),
            "scores": event.get("scores", {}),
            "timestamp": datetime.utcnow()
        }

        self.memory.store(normalized)

    def learn(self, signal: dict):
        """
        Learning hook (future: pattern mining, reinforcement, adaptation)
        """
        # Placeholder for learning algorithms
        self.observe(None, signal)

    def reinforce(self, signal: dict):
        """
        Reinforcement hook (future: behavior shaping, optimization)
        """
        # Placeholder for reinforcement logic
        self.observe(None, signal)

    def snapshot(self):
        """
        Return current learning memory snapshot
        """
        events = self.memory.fetch_all()
        return {
            "memory": {
                "events": len(events),
                "data": events
            }
        }
