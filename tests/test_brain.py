from support_agent import brain
from support_agent.brain import parse_response

class MockResponse:
    def __init__(self, status_code, data=None, headers=None):
        self.status_code = status_code
        self.data = data
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise brain.requests.exceptions.HTTPError(response=self)

    def json(self):
        return self.data


def test_text_answer_is_translated():
    response = {"choices": [{"message": {"content": "Hi there", "tool_calls": None}}]}
    assert parse_response(response) == {"answer" : "Hi there"}

def test_tool_request_is_translated():
    response = {"choices": [{"message": {
        "content": None,
        "tool_calls": [{"id" : "call_1", "function": {
            "name": "get_order_status",
            "arguments": '{"order_id":"ORD-2001"}'
        }}]
    }}]}
    result = parse_response(response)
    assert result == {
        "tool": "get_order_status",
        "args": {"order_id": "ORD-2001"},
        "id": "call_1"
    }
    assert result["id"] == "call_1"

def test_tool_call_wins_even_if_text_present():
    response = {"choices": [{"message": {
        "content": "Let me check that.",
        "tool_calls": [{"id" : "call_1","function": {
            "name": "get_order_status",
            "arguments": '{"order_id":"ORD-2001"}'
        }}]
    }}]}
    assert parse_response(response)["tool"] == "get_order_status"

def test_call_fails_once_with_a_500_then_succeeds(monkeypatch):
    reply = [MockResponse(status_code=500), MockResponse(status_code=200, data={"ok": True})]
    monkeypatch.setattr(brain.requests, "post", lambda *a, **k: reply.pop(0))
    monkeypatch.setattr(brain.time, "sleep", lambda seconds: None)
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    assert brain.call_openai([], []) == {"ok": True}


