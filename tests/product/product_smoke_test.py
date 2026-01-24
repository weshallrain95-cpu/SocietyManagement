from society_product.api.gateway.router import ProductAPIGateway

# Dummy request object to simulate HTTP request
class DummyRequest:
    def __init__(self):
        self.headers = {
            "X-User-ID": "user123",
            "X-Society-ID": "society456"
        }

def test_finance_collect_due_flow():
    req = DummyRequest()

    result = ProductAPIGateway.dispatch(
        request=req,
        domain="finance",
        action="collect_due",
        payload={"amount": 1000}
    )

    # Flow validation
    assert result is not None
    assert result["status"] == "success"
    assert result["action"] == "collect_due"
    assert result["society_id"] == "society456"
    assert result["amount"] == 1000


def test_finance_approve_payment_flow():
    req = DummyRequest()

    result = ProductAPIGateway.dispatch(
        request=req,
        domain="finance",
        action="approve_payment",
        payload={"payment_id": "pay_001"}
    )

    assert result is not None
    assert result["status"] == "approved"
    assert result["payment_id"] == "pay_001"
