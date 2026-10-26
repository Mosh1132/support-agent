import json
from functools import partial
from support_agent.tools import get_order_status, refund_order
from support_agent.retrieval import search_handbook

def build_tools(connection, index):
    return {
        "get_order_status": partial(get_order_status, connection=connection),
        "refund_order": partial(refund_order, connection=connection),
        "search_handbook": partial(search_handbook, index=index),
    }

def run_agent(question, brain, tools, history, max_steps=5):
    history.append({"role" : "user", "content" : question})
    for _ in range(max_steps):
        decision = brain(history)
        if "answer" in decision:
            return decision["answer"]
        if "tool" in decision:
            func = tools.get(decision["tool"])
            if func is None:
                result = {"success": False, "error": f"Unknown tool: {decision['tool']}"}
            else:
                args = decision["args"]
                try:
                    result = func(**args)
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