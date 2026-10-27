import json
from support_agent.agent import run_agent, build_policy_tools, build_orders_tools

def test_agent_returns_direct_answer(connection):
    tools = build_policy_tools(None)
    def brain(messages):
        return {"answer": "Hello"}
    assert run_agent("hi", brain, tools, []) == "Hello"

def test_agent_calls_tool_then_answers(connection):
    tools = build_orders_tools(connection)
    def brain(messages):
        if messages[-1]["role"] == "tool":
            return {"answer": "Status: " + json.loads(messages[-1]["content"])["status"]}
        return {"tool": "get_order_status", "args": {"order_id": "ORD-2001"}, "id": "call_1"}
    assert run_agent("where is ORD-2001?", brain, tools, []) == "Status: Order Placed"

def test_agent_stops_after_max_steps(connection):
    tools = build_policy_tools(None)
    def brain(messages):
        return {"tool": "get_order_status", "args": {"order_id": "ORD-2001"}, "id": "call_1"}
    result = run_agent("loop forever", brain, tools,  [], max_steps=3)
    assert "human" in result.lower()

def test_tool_result_is_stored_as_text(connection):
    seen = []
    tools = build_policy_tools(None)
    def brain(messages):
        seen.append(messages[-1])
        if messages[-1]["role"] == "tool":
            return {"answer": "done"}
        return {"tool": "get_order_status", "args": {"order_id": "ORD-2001"}, "id": "call_1"}

    run_agent("where is ORD-2001?", brain, tools, [])

    tool_message = seen[-1]
    assert isinstance(tool_message["content"], str)

def test_tool_messages_carry_the_call_id(connection):
    seen = []
    tools = build_policy_tools(None)
    def brain(messages):
        seen.append(list(messages))
        if messages[-1]["role"] == "tool":
            return {"answer": "done"}
        return {
            "tool": "get_order_status",
            "args": {"order_id": "ORD-2001"},
            "id" : "call_1"
        }

    run_agent("where is ORD-2001?", brain, tools, [])

    last = seen[-1]
    assert last[-2]["role"] == "assistant"
    assert last[-1]["tool_call_id"] == "call_1"

def test_tool_does_not_crash_when_non_existent_tool_is_called(connection):
    tools = build_policy_tools(None)
    def brain(messages):
        if messages[-1]["role"] == "tool":
            return {"answer": "recovered"}
        return {"tool": "delete_everything", "args": {}, "id": "call_1"}

    result = run_agent("do something bad", brain,tools, [])
    assert result == "recovered"

def test_tool_message_contains_tool_name(connection):
    seen = []
    tools = build_policy_tools(None)
    def brain(messages):
        seen.extend(messages)
        if messages[-1]["role"] == "tool":
            return {"answer": "recovered"}
        return {"tool": "launch_rockets", "args": {}, "id": "call_1"}

    run_agent("do something", brain, tools, [])

    tool_message = seen[-1]
    assert "launch_rockets" in tool_message["content"]

def test_tool_does_not_crash_when_non_existent_arg_is_called(connection):
    tools = build_policy_tools(None)
    def brain(messages):
        if messages[-1]["role"] == "tool":
            return {"answer": "recovered"}
        return {"tool": "get_order_status", "args": {"wrong_name" : "x"}, "id": "call_1"}

    result = run_agent("do something", brain, tools, [])

    assert result == "recovered"

def test_policy_tools_contains_only_search_handbook():
    tools = build_policy_tools(None)
    assert "get_order_status" not in tools
    assert "refund_order" not in tools
    assert "search_handbook" in tools



