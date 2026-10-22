import json

from support_agent.tools import get_order_status, refund_order

TOOLS = {"get_order_status": get_order_status, "refund_order": refund_order}

def run_agent(question, brain, connection, max_steps=5):
    messages = [{"role" : "user", "content" : question}]
    for _ in range(max_steps):
        decision = brain(messages)
        if "answer" in decision:
            return decision["answer"]
        if "tool" in decision:
            func = TOOLS.get(decision["tool"])
            args = decision["args"]
            result = func(**args, connection=connection)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": decision["id"],
                    "type": "function",
                    "function": {
                        "name": decision["tool"],
                        "arguments": json.dumps(decision["args"]),
                    },
                }],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": decision["id"],
                "content": json.dumps(result),
            })
    return "Sorry, I couldn't finish this. A human will follow up."