from support_agent.tools import get_order_status, refund_order

def test_lowercase_order_id_is_accepted():
    result = get_order_status("ord-2001")
    assert result["found"] is True, result

def test_extra_spaces_are_ignored():
    result = get_order_status("  ORD-2001  ")
    assert result["found"] is True, result

def test_garbage_input_is_rejected():
    result = get_order_status("DROP TABLE orders")
    assert result["found"] is False

def test_non_string_input_is_rejected():
    result = get_order_status(12345)
    assert result["found"] is False

def test_refund_rejects_garbage_id():
    result = refund_order("DROP TABLE orders")
    assert result["success"] is False