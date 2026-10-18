from support_agent.tools import get_order_status

def test_known_order_returns_status():
    assert get_order_status("ORD-2001") == "Order Placed"

def test_unknown_order_returns_not_found():
    assert get_order_status("FAKE-999") == "order not found"