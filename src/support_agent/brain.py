import json

def parse_response(response):
    message = response['choices'][0]['message']
    if message.get("tool_calls"):
        tool_calls = message['tool_calls']
        function = tool_calls[0]['function']
        return {"tool" : function['name'], "args" : json.loads(function['arguments'])}
    return {"answer" : message['content']}