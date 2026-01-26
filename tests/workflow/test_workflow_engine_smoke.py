from society_product.workflow_engine.process_graph import ProcessGraph, Node
from society_product.workflow_engine.engine import WorkflowEngine

# Reuse DummyRequest from product smoke tests
from tests.product.product_smoke_test import DummyRequest
from society_product.api.gateway.context import ProductContextBuilder

def test_onboarding_workflow_end_to_end():
    # Build a tiny onboarding workflow: add_member -> create_task -> send_notice
    nodes = [
        Node(node_id="n1", action_domain="members", action_name="add_member", params={"name": "Kumar"}),
        Node(node_id="n2", action_domain="operations", action_name="create_task", params={"task": "WelcomeCall"}),
        Node(node_id="n3", action_domain="communications", action_name="send_notice", params={"message": "Welcome Kumar!"})
    ]
    graph = ProcessGraph(graph_id="onboarding-v1", nodes=nodes)

    # create request and context
    req = DummyRequest()
    ctx = ProductContextBuilder.build(req)

    # attach original request to context for dispatcher identity reuse
    setattr(ctx, "_request_like", req)

    engine = WorkflowEngine()
    result = engine.run(graph, ctx, initial_payload={})

    assert result["status"] == "completed"
    assert "n1" in result["results"]
    assert "n2" in result["results"]
    assert "n3" in result["results"]
