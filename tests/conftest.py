import pytest
from support_agent.db import seed_orders, get_connection

@pytest.fixture
def connection():
    conn = get_connection(":memory:")
    seed_orders(conn)
    return conn