import sqlite3

SAMPLE_ORDERS = [
    ("ORD-2001", "Order Placed", 89.99, "Emma Watson", "emma@example.com"),
    ("ORD-2006", "Delivered", 120.00, "James Brown", "james@example.com"),
    ("ORD-2011", "Refunded", 62.10, "Harper Thomas", "harper@example.com"),
    ("ORD-2012", "Delivered", 45.00, "Mia Taylor", "mia@example.com"),
    ("ORD-2013", "Delivered", 100.00, "Leo Park", "leo@example.com"),
]

def get_connection(path="orders.db"):
    connec = sqlite3.connect(path)
    connec.execute(
        "CREATE TABLE IF NOT EXISTS orders "
        "(order_id TEXT PRIMARY KEY, delivery_status TEXT, "
        "price REAL,  customer_name TEXT, customer_email TEXT)"
    )
    return connec

def seed_orders(connection):
    count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    if count > 0:
        return
    connection.executemany(
        "INSERT INTO orders VALUES(?, ?, ?, ?, ?)", SAMPLE_ORDERS
    )
    connection.commit()