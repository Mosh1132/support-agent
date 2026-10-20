import sqlite3

def get_connection(path="orders.db"):
    connec = sqlite3.connect(path)
    connec.execute("CREATE TABLE IF NOT EXISTS orders (order_ID TEXT PRIMARY KEY, delivery_status TEXT, price REAL,  customer_name TEXT, customer_email TEXT)")
    return connec