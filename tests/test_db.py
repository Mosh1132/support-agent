from support_agent.db import get_connection

def test_get_connection_db():
    connec = get_connection(":memory:")

    connec.execute(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?)", ("ORD-2001",
                                                      "Out for Delivery", 125.99, "Timi Tella",
                                                      "timitella@gmail.com")
    )

    row = connec.execute(
        "SELECT customer_name FROM orders WHERE order_id = ?", ("ORD-2001",)
    ).fetchone()
    connec.commit()
    assert row[0] == "Timi Tella"
