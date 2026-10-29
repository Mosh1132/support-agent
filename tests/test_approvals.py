from support_agent.approvals import decide_approval, list_pending_approvals
from support_agent.tools import get_order_status, refund_order

def test_approving_refunds_the_order(connection):
    refund_order("ORD-2006", connection)
    approval_id = list_pending_approvals(connection)[0]["id"]

    result = decide_approval(approval_id, "approved", connection)

    assert result["success"] is True
    assert get_order_status("ORD-2006", connection)["status"] == "Refunded"


def test_rejecting_leaves_the_order_unchanged(connection):
    refund_order("ORD-2006", connection)
    approval_id = list_pending_approvals(connection)[0]["id"]

    result = decide_approval(approval_id, "rejected", connection)

    assert result["success"] is True
    assert get_order_status("ORD-2006", connection)["status"] == "Delivered"
    assert list_pending_approvals(connection) == []


def test_same_request_cannot_be_decided_twice(connection):
    refund_order("ORD-2006", connection)
    approval_id = list_pending_approvals(connection)[0]["id"]

    decide_approval(approval_id, "rejected", connection)
    second = decide_approval(approval_id, "approved", connection)

    assert second["success"] is False
    assert get_order_status("ORD-2006", connection)["status"] == "Delivered"


def test_unknown_approval_id_is_rejected(connection):
    result = decide_approval(999, "approved", connection)
    assert result["success"] is False