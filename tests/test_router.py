from support_agent.router import route_question


def test_orders_label_routes_to_orders():
    assert route_question("Where is ORD-2001?", lambda q: "orders") == "orders"


def test_label_is_cleaned_before_use():
    assert route_question("What is your policy?", lambda q: "  Policy\n") == "policy"


def test_unknown_label_falls_back_to_policy():
    assert route_question("anything", lambda q: "banana") == "policy"