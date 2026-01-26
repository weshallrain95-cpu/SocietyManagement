class IntelligenceInfluenceEngine:
    """
    Converts learning memory into behavioral influence.
    This is where the system adapts its own execution logic.
    """

    def __init__(self, learning_engine):
        self.learning = learning_engine

    def snapshot(self):
        return {
            "weights": getattr(self, "weights", {}),
            "rules": len(getattr(self, "rules", [])),
            "mode": "learning_influence",
        }


    def influence_scoring(self, base_scores: dict, context: dict):
        """
        Modify scoring based on learned patterns
        """
        memory = self.learning.snapshot()["memory"]["data"]

        adjusted = base_scores.copy()

        for event in memory:
            if event.get("event_type") == "failure":
                adjusted["risk"] = min(1.0, adjusted.get("risk", 0.0) + 0.05)

            if event.get("event_type") == "success":
                adjusted["confidence"] = min(1.0, adjusted.get("confidence", 0.0) + 0.05)

        return adjusted

    def influence_routing(self, candidates: list, context: dict):
        """
        Influence node/workflow selection
        """
        memory = self.learning.snapshot()["memory"]["data"]

        if not memory:
            return candidates

        # simple adaptive filtering
        bad_nodes = {
            e.get("node_id") for e in memory if e.get("event_type") == "failure"
        }

        filtered = [c for c in candidates if c not in bad_nodes]

        return filtered or candidates  # never deadlock system

    def influence_execution(self, decision: dict, context: dict):
        """
        Influence execution decisions
        """
        scores = decision.get("scores", {})

        if scores.get("risk", 0) > 0.7:
            decision["mode"] = "human_review"
        elif scores.get("confidence", 0) > 0.8:
            decision["mode"] = "auto_execute"
        else:
            decision["mode"] = "standard"

        return decision
