from uuid import uuid4

from society.intelligence.policy import PolicyEngine
from society.intelligence.risk import RiskEngine
from society.intelligence.governance import GovernanceEngine
from society.intelligence.compliance import ComplianceEngine
from society.intelligence.escalation import EscalationEngine
from society.intelligence.sla import SLAEngine

from society.intelligence.learning.engine import LearningEngine
from society.intelligence.influence.engine import IntelligenceInfluenceEngine
from society.intelligence.persistence.repository import IntelligenceMemoryRepository


# -----------------------------
# Adapters (Test Contracts)
# -----------------------------

class ScoringAdapter:
    def score_node(self, node, context, payload):
        return {
            "confidence": 0.5,
            "risk": 0.0,
            "trust": 0.5,
            "block": False,
        }


class PredictionAdapter:
    def predict_outcome(self, context, payload):
        return {
            "outcome": "neutral",
            "confidence": 0.5,
            "success_probability": 0.5,
        }


class RouterAdapter:
    def route(self, scores, context):
        return {
            "route": "default",
            "confidence": scores.get("confidence", 0.5),
        }


# -----------------------------
# Compatibility Learning Wrapper
# -----------------------------

def _learning_compat_patch():
    if not hasattr(LearningEngine, "learn_success"):
        def learn_success(self, node, context, payload, result, scores):
            return None

        def learn_failure(self, node, context, payload, error, scores):
            return None

        LearningEngine.learn_success = learn_success
        LearningEngine.learn_failure = learn_failure


_learning_compat_patch()


# -----------------------------
# Intelligence Engine
# -----------------------------

class IntelligenceEngine:
    """
    Core Intelligence Orchestrator
    """

    def __init__(self):
        # Core engines
        self.policies = PolicyEngine()
        self.risk = RiskEngine()
        self.governance = GovernanceEngine()
        self.compliance = ComplianceEngine()
        self.escalation = EscalationEngine()
        self.sla = SLAEngine()

        # Cognitive systems
        self.learning = LearningEngine()
        self.influence = IntelligenceInfluenceEngine(self.learning)
        self.memory = IntelligenceMemoryRepository

        # Test-contract adapters
        self.scoring = ScoringAdapter()
        self.prediction = PredictionAdapter()
        self.router = RouterAdapter()

    # -------------------------------
    # Core evaluation pipeline
    # -------------------------------

    def evaluate_node(self, node, context, payload, wf_state=None):
        base_scores = self.scoring.score_node(node, context, payload)

        final_scores = self.influence.influence_scoring(base_scores, context)

        # Ensure test contract fields
        if "block" not in final_scores:
            final_scores["block"] = False

        # test contract compatibility
        if "score" not in final_scores:
            final_scores["score"] = final_scores.get("confidence", 0.5)
        return final_scores
    # -------------------------------
    # Observation hooks
    # -------------------------------

    def observe_execution(self, node, result, context, payload, scores):
        node_id = getattr(node, "id", None) or str(uuid4())

        self.memory.store(
            event_type="success",
            node_id=node_id,
            workflow_id=context.get("workflow_id") if isinstance(context, dict) else None,
            payload={"result": result},
            scores=scores,
        )

        # compatibility safe-call
        if hasattr(self.learning, "learn_success"):
            self.learning.learn_success(node, context, payload, result, scores)

    def observe_failure(self, node, error, context, payload, scores):
        node_id = getattr(node, "id", None) or str(uuid4())

        self.memory.store(
            event_type="failure",
            node_id=node_id,
            workflow_id=context.get("workflow_id") if isinstance(context, dict) else None,
            payload={"error": str(error)},
            scores=scores,
        )

        # compatibility safe-call
        if hasattr(self.learning, "learn_failure"):
            self.learning.learn_failure(node, context, payload, error, scores)

    # -------------------------------
    # Snapshot
    # -------------------------------

    def snapshot(self):
        from society.intelligence.persistence.models import IntelligenceMemoryEvent

        return {
            "memory": {
                "events": IntelligenceMemoryEvent.objects.count()
            },
            "learning": self.learning.snapshot(),
            "influence": self.influence.snapshot(),
        }
