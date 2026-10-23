import json

from support_agent.tools import get_order_status, refund_order

TOOLS = {"get_order_status": get_order_status, "refund_order": refund_order}

def run_agent(question, brain, connection, history, max_steps=5):
    history.append({"role" : "user", "content" : question})
    for _ in range(max_steps):
        decision = brain(history)
        if "answer" in decision:
            return decision["answer"]
        if "tool" in decision:
            func = TOOLS.get(decision["tool"])
            if func is None:
                result = {"success": False, "error": f"Unknown tool: {decision['tool']}"}
            else:
                args = decision["args"]
                try:
                    result = func(**args, connection=connection)
                except TypeError:
                    result = {"success": False, "error": f"Invalid arguments for {decision['tool']}"}
            history.append({
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
            history.append({
                "role": "tool",
                "tool_call_id": decision["id"],
                "content": json.dumps(result),
            })
    return "Sorry, I couldn't finish this. A human will follow up."