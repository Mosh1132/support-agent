import re
REFUND_LIMIT = 100
DATABASE = {
    "ORD-2001": {"delivery_status": "Order Placed", "price": 89.99,
                 "customer_name": "Emma Watson", "customer_email": "emma@example.com"},
    "ORD-2006": {"delivery_status": "Delivered", "price": 120.00,
                 "customer_name": "James Brown", "customer_email": "james@example.com"},
    "ORD-2011": {"delivery_status": "Refunded", "price": 62.10,
                 "customer_name": "Harper Thomas", "customer_email": "harper@example.com"},
    "ORD-2012": {"delivery_status": "Delivered", "price": 45.00,
                 "customer_name": "Mia Taylor", "customer_email": "mia@example.com"},
    "ORD-2013": {"delivery_status": "Delivered", "price": 100.00,
                 "customer_name": "Leo Park", "customer_email": "leo@example.com"},
}

def get_order_status(order_id):
    clean_id = normalize_order_id(order_id)
    if clean_id is None:
        return {"found": False, "error": "Invalid order ID format"}
    order = DATABASE.get(clean_id, None)
    if order is None:
        return {"found" : False, "error": f"Order {order_id} does not exist"}
    return {"found" : True, "status" : order["delivery_status"]}

def refund_order(order_id):
    order = DATABASE.get(order_id, None)
    if order is None:
        return {"success" : False, "needs_human": False, "error": f"Order {order_id} does not exist"}
    if order["delivery_status"] != "Delivered":
        return {"success": False, "needs_human": False, "error": f"Order {order_id} cannot be refunded"}
    if order["price"] > REFUND_LIMIT:
        return {"success": False, "needs_human": True, "message": f"Refund of ${order['price']} needs manager approval"}
    return {"success": True, "needs_human": False, "message": f"Refund of ${order['price']} issued for order {order_id}"}

def normalize_order_id(order_id):
    if not isinstance(order_id, str):
        return None
    cleaned = order_id.strip().upper()
    if re.fullmatch(r"ORD-\d+", cleaned):
        return cleaned
    return None