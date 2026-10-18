from support_agent.agent import run_agent

def test_agent_returns_direct_answer():
    def brain(messages):
        return {"answer": "Hello"}
    assert run_agent("hi", brain) == "Hello"

def test_agent_calls_tool_then_answers():
    def brain(messages):
        if messages[-1]["role"] == "tool":
            return {"answer": "Status: " + messages[-1]["content"]["status"]}
        return {"tool": "get_order_status", "args": {"order_id": "ORD-2001"}}
    assert run_agent("where is ORD-2001?", brain) == "Status: Order Placed"

def test_agent_stops_after_max_steps():
    def brain(messages):
        return {"tool": "get_order_status", "args": {"order_id": "ORD-2001"}}
    result = run_agent("loop forever", brain, max_steps=3)
    assert "human" in result.lower()