DATABASE = {
    "ORD-2001": {
        "delivery_status": "Order Placed",
        "price": 89.99,
        "customer_name": "Emma Watson",
        "customer_email": "emma@example.com",
    },
}

def get_order_status(order_id):
    order = DATABASE.get(order_id, None)
    if order is None:
        return "order not found"
    return order["delivery_status"]