from support_agent.tools import get_order_status, refund_order

def test_known_order_returns_status(connection):
    result = get_order_status("ORD-2001", connection)
    assert result["found"] is True
    assert result["status"] == "Order Placed"

def test_unknown_order_returns_not_found(connection):
    result = get_order_status("ORD-9999", connection)
    assert result["found"] is False
    assert "ORD-9999" in result["error"]

def test_result_does_not_leak_customer_email(connection):
    result = get_order_status("ORD-2001", connection)
    assert "emma@example.com" not in str(result)

def test_already_refunded_order_is_rejected(connection):
    result = refund_order("ORD-2011", connection)
    assert result["success"] is False

def test_unknown_order_refund_is_rejected(connection):
    result = refund_order("FAKE-999", connection)
    assert result["success"] is False

def test_successful_refund_has_no_error(connection):
    result = refund_order("ORD-2006", connection)
    assert "error" not in result

def test_small_delivered_refund_succeeds(connection):
    result = refund_order("ORD-2012", connection)
    assert result["success"] is True

def test_large_refund_needs_human(connection):
    result = refund_order("ORD-2006", connection)
    assert result["success"] is False
    assert result["needs_human"] is True

def test_refund_exactly_at_limit_is_allowed(connection):
    result = refund_order("ORD-2013", connection)
    assert result["success"] is True, result

def test_refund_unknown_valid_id_is_rejected(connection):
    result = refund_order("ORD-9999", connection)
    assert result["success"] is False

def test_refund_creates_pending_approval(connection):
    refund_order("ORD-2006", connection)
    row = connection.execute("SELECT order_id, status FROM approvals").fetchall()
    assert row == [("ORD-2006", "pending")]

def test_order_does_not_get_refunded_twice(connection):
    refund_order("ORD-2012", connection)
    refund = refund_order("ORD-2012", connection)
    assert refund["success"] == False

def test_refund_creates_only_one_pending_approval(connection):
    refund_order("ORD-2006", connection)
    refund_order("ORD-2006", connection)
    row = connection.execute("SELECT COUNT(*) FROM "
                             "approvals").fetchone()[0]

    assert row == 1