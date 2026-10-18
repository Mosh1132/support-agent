from support_agent.tools import get_order_status, refund_order

def test_known_order_returns_status():
    result = get_order_status("ORD-2001")
    assert result["found"] is True
    assert result["status"] == "Order Placed"

def test_unknown_order_returns_not_found():
    result = get_order_status("ORD-9999")
    assert result["found"] is False
    assert "ORD-9999" in result["error"]

def test_result_does_not_leak_customer_email():
    result = get_order_status("ORD-2001")
    assert "emma@example.com" not in str(result)

def test_already_refunded_order_is_rejected():
    result = refund_order("ORD-2011")
    assert result["success"] is False

def test_unknown_order_refund_is_rejected():
    result = refund_order("FAKE-999")
    assert result["success"] is False

def test_successful_refund_has_no_error():
    result = refund_order("ORD-2006")
    assert "error" not in result

def test_small_delivered_refund_succeeds():
    result = refund_order("ORD-2012")
    assert result["success"] is True

def test_large_refund_needs_human():
    result = refund_order("ORD-2006")
    assert result["success"] is False
    assert result["needs_human"] is True

def test_refund_exactly_at_limit_is_allowed():
    result = refund_order("ORD-2013")
    assert result["success"] is True, result

def test_refund_unknown_valid_id_is_rejected():
    result = refund_order("ORD-9999")
    assert result["success"] is False