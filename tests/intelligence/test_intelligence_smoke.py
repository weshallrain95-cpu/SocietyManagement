import pytest
from society.intelligence.bootstrap import build_intelligence


class DummyNode:
    def __init__(self, node_id="N1"):
        self.node_id = node_id


class DummyGraph:
    def get_next_nodes(self, node_id):
        return []


@pytest.mark.django_db
def test_intelligence_bootstrap():
    engine = build_intelligence()
    assert engine is not None
    assert engine.memory is not None
    assert engine.scoring is not None
    assert engine.policies is not None
    assert engine.prediction is not None
    assert engine.router is not None


@pytest.mark.django_db
def test_intelligence_node_evaluation():
    engine = build_intelligence()
    node = DummyNode()
    ctx = {}
    payload = {}
    wf_state = {}

    result = engine.evaluate_node(node, ctx, payload, wf_state)
    assert "block" in result
    assert "score" in result
    assert result["block"] is False


@pytest.mark.django_db
def test_intelligence_memory_recording():
    engine = build_intelligence()
    node = DummyNode()

    engine.observe_execution(node, {"ok": True}, {}, {}, {})
    engine.observe_failure(node, Exception("fail"), {}, {}, {})

    snapshot = engine.snapshot()
    assert snapshot["memory"]["events"] == 2


@pytest.mark.django_db
def test_intelligence_prediction():
    engine = build_intelligence()
    result = engine.prediction.predict_outcome({}, {})
    assert "success_probability" in result
