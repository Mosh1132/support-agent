def route_question(question, classify):
    label = classify(question).strip().lower()
    if label == "orders":
        return "orders"
    return "policy"