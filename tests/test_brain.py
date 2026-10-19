from support_agent.brain import parse_response

def test_text_answer_is_translated():
    response = {"choices": [{"message": {"content": "Hi there", "tool_calls": None}}]}
    assert parse_response(response) == {"answer" : "Hi there"}

def test_tool_request_is_translated():
    response = {"choices": [{"message": {
        "content": None,
        "tool_calls": [{"function": {
            "name": "get_order_status",
            "arguments": '{"order_id":"ORD-2001"}'
        }}]
    }}]}
    assert parse_response(response) == {
        "tool": "get_order_status",
        "args": {"order_id": "ORD-2001"},
    }

def test_tool_call_wins_even_if_text_present():
    response = {"choices": [{"message": {
        "content": "Let me check that.",
        "tool_calls": [{"function": {
            "name": "get_order_status",
            "arguments": '{"order_id":"ORD-2001"}'
        }}]
    }}]}
    assert parse_response(response)["tool"] == "get_order_status"