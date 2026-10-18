DATABASE = {
    "ORD-2001": {"delivery_status": "Order Placed", "price": 89.99,
                 "customer_name": "Emma Watson", "customer_email": "emma@example.com"},
    "ORD-2006": {"delivery_status": "Delivered", "price": 120.00,
                 "customer_name": "James Brown", "customer_email": "james@example.com"},
    "ORD-2011": {"delivery_status": "Refunded", "price": 62.10,
                 "customer_name": "Harper Thomas", "customer_email": "harper@example.com"},
}

def get_order_status(order_id):
    order = DATABASE.get(order_id, None)
    if order is None:
        return {"found" : False, "error": f"Order {order_id} does not exist"}
    return {"found" : True, "status" : order["delivery_status"]}

def refund_order(order_id):
    order = DATABASE.get(order_id, None)
    if order is None:
        return {"success" : False, "error": f"Order {order_id} does not exist"}
    if order["delivery_status"] != "Delivered":
        return {"success": False, "error": f"Order {order_id} cannot be refunded"}
    return {"success": True, "error": f"Refund issued for order {order_id}"}
