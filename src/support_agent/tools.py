import re

REFUND_LIMIT = 100

def get_order_status(order_id, connection):
    clean_id = normalize_order_id(order_id)
    if clean_id is None:
        return {"found": False, "error": "Invalid order ID format"}
    row = connection.execute("SELECT delivery_status FROM orders WHERE order_id = ?", (clean_id,)).fetchone()
    if row is None:
        return {"found" : False, "error": f"Order {clean_id} does not exist"}
    return {"found" : True, "status" : row[0]}

def refund_order(order_id, connection):
    clean_id = normalize_order_id(order_id)
    if clean_id is None:
        return {"success": False, "needs_human": False, "error": "Invalid order ID format"}
    row = connection.execute("SELECT delivery_status, price FROM orders WHERE order_id = ?", (clean_id,)).fetchone()
    if row is None:
        return {"success" : False, "needs_human": False, "error": f"Order {clean_id} does not exist"}
    if row[0] != "Delivered":
        return {"success": False, "needs_human": False, "error": f"Order {clean_id} cannot be refunded"}
    if row[1] > REFUND_LIMIT:
        existing = connection.execute("SELECT 1 FROM approvals WHERE "
                                     "order_id = ? AND status = "
                                      "'pending'", (clean_id,)).fetchone()
        if existing is None:
            connection.execute("INSERT INTO approvals (order_id, "
                               "amount, status) VALUES (?, ?, ?)",
                               (clean_id, row[1], 'pending'))
            connection.commit()
        return {"success": False, "needs_human": True, "message": f"Refund of ${row[1]} can ONLY be decided by manager if approved."}
    connection.execute("UPDATE orders SET delivery_status "
             "= ? WHERE order_id = ?", ("Refunded", clean_id))
    connection.commit()
    return {"success": True, "needs_human": False, "message": f"Refund of ${row[1]} issued for order {clean_id}"}

def normalize_order_id(order_id):
    if not isinstance(order_id, str):
        return None
    cleaned = order_id.strip().upper()
    if re.fullmatch(r"ORD-\d+", cleaned):
        return cleaned
    return None