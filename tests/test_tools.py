from support_agent.tools import get_order_status

def test_known_order_returns_status():
    result = get_order_status("ORD-2001")
    assert result["found"] is True
    assert result["status"] == "Order Placed"

def test_unknown_order_returns_not_found():
    result = get_order_status("FAKE-999")
    assert result["found"] is False
    assert "FAKE-999" in result["error"]

def test_result_does_not_leak_customer_email():
    result = get_order_status("ORD-2001")
    assert "emma@example.com" not in str(result)