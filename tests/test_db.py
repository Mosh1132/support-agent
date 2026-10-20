from support_agent.db import get_connection, seed_orders

def test_get_connection_db():
    connec = get_connection(":memory:")

    connec.execute(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)", ("ORD-2001",
                                                      "Out for Delivery", 125.99, "Timi Tella",
                                                      "timitella@gmail.com")
    )

    row = connec.execute(
        "SELECT customer_name FROM orders WHERE order_id = ?",
        ("ORD-2001",)
    ).fetchone()
    connec.commit()
    assert row[0] == "Timi Tella"


def test_seed_orders():
    connection = get_connection(":memory:")
    seed_orders(connection)

    row = connection.execute(
        "SELECT delivery_status FROM orders WHERE order_id = ?",
        ("ORD-2006",)
    ).fetchone()

    assert row[0] == "Delivered"

def test_calling_seed_orders_twice_does_not_cause_a_crash():
    connection = get_connection(":memory:")
    seed_orders(connection)
    seed_orders(connection)
    count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    assert count == 5