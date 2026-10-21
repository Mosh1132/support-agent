from support_agent.tools import get_order_status, refund_order

def test_lowercase_order_id_is_accepted(connection):
    result = get_order_status("ord-2001", connection)
    assert result["found"] is True, result

def test_extra_spaces_are_ignored(connection):
    result = get_order_status("  ORD-2001  ", connection)
    assert result["found"] is True, result

def test_garbage_input_is_rejected(connection):
    result = get_order_status("DROP TABLE orders", connection)
    assert result["found"] is False

def test_non_string_input_is_rejected(connection):
    result = get_order_status(12345, connection)
    assert result["found"] is False

def test_refund_rejects_garbage_id(connection):
    result = refund_order("DROP TABLE orders", connection)
    assert result["success"] is False
    assert "Invalid" in result["error"]

def test_refund_missing_order_says_does_not_exist(connection):
    result = refund_order("ORD-9999", connection)
    assert "does not exist" in result["error"]
