def list_pending_approvals(connection):
    rows = connection.execute(
        "SELECT * FROM approvals WHERE status = 'pending'"
    ).fetchall()
    return [{"id": r[0], "order_id": r[1], "amount": r[2]} for r in rows]
def decide_approval(approval_id, decision, connection):
    if decision not in ("approved", "rejected"):
        return {"success": False, "error": "Decision must be 'approved' or 'rejected'"}
    row = connection.execute(
        "SELECT order_id FROM approvals WHERE id = ? AND status = 'pending'",
        (approval_id,),
    ).fetchone()
    if row is None:
        return {"success": False, "error": f"No pending approval with id {approval_id}"}
    connection.execute(
        "UPDATE approvals SET status = ? WHERE id = ?", (decision, approval_id)
    )
    if decision == "approved":
        connection.execute(
            "UPDATE orders SET delivery_status = 'Refunded' WHERE order_id = ?",
            (row[0],),
        )
    connection.commit()
    return {"success": True, "approval_id": approval_id, "decision": decision}