import pytest
from society.intelligence.bootstrap import build_intelligence
from society.intelligence.influence.engine import IntelligenceInfluenceEngine


@pytest.mark.django_db
def test_learning_influences_scoring():
    engine = build_intelligence()
    influence = IntelligenceInfluenceEngine(engine.learning)

    base = {"risk": 0.2, "confidence": 0.5}

    engine.learning.observe(None, {
        "event_type": "failure",
        "node_id": "N1"
    })

    adjusted = influence.influence_scoring(base, {})

    assert adjusted["risk"] > base["risk"]


@pytest.mark.django_db
def test_learning_influences_routing():
    engine = build_intelligence()
    influence = IntelligenceInfluenceEngine(engine.learning)

    engine.learning.observe(None, {
        "event_type": "failure",
        "node_id": "N2"
    })

    candidates = ["N1", "N2", "N3"]
    routed = influence.influence_routing(candidates, {})

    assert "N2" not in routed
