from support_agent.db import get_connection, seed_orders
from support_agent.tools import refund_order

right = get_connection(":memory:")
seed_orders(right)

print(right.execute("SELECT * FROM orders").fetchall())

# refund_order("ORD-2006", right)
# refund_order("ORD-2013", right)
# print(right.execute("SELECT * FROM approvals").fetchmany())
