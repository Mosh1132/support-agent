import json
import requests
from support_agent.config import get_api_key

def parse_response(response):
    message = response['choices'][0]['message']
    if message.get("tool_calls"):
        tool_calls = message['tool_calls']
        function = tool_calls[0]['function']
        return {"tool" : function['name'], "args" : json.loads(function['arguments'])}
    return {"answer" : message['content']}

def call_openai(messages, tools):
    response = requests.post('https://api.openai.com/v1/chat/completions',
                             headers={
                                 'Authorization': f'Bearer {get_api_key()}',
                                 'Content-Type': 'application/json'
                             },
                             json={
                                 "model" : "gpt-4o-mini",
                                 "messages" : messages,
                                 "tools" : tools,
                             }, timeout=30)

    response.raise_for_status()
    return response.json()