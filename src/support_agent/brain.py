import json
import time
import random
import logging
import requests
from support_agent.config import get_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TOOL_DEFINITIONS = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_order_status",
            "description" : "Look up the delivery status of an order by its order ID.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "order_id" : {"type" : "string", "description" : "e.g. ORD-2001"},
                },
                "required" : ["order_id"]
            }
        }
    },
{
        "type" : "function",
        "function" : {
            "name" : "refund_order",
            "description" : "ONLY call this when the customer clearly asks you to refund an order. Do not call it for questions about whether a refund is possible.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "order_id" : {"type" : "string", "description" : "e.g. ORD-2001"},
                },
                "required" : ["order_id"]
            }
        }
    },
{
        "type" : "function",
        "function" : {
            "name" : "search_handbook",
            "description" : "Search the company policy handbook for rules about refunds, returns, cancellations, and shipping. Use this to answer policy questions. Do not use it to look up or change a specific order.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "question" : {"type" : "string",
                                  "description" : "The customer's policy question, e.g. 'How long does shipping take?'"},
                },
                "required" : ["question"]
            }
        }
    },
]

ORDERS_DEFINITIONS = [d for d in TOOL_DEFINITIONS if d["function"]["name"] in ("get_order_status", "refund_order")]
POLICY_DEFINITIONS = [d for d in TOOL_DEFINITIONS if d["function"]["name"] == "search_handbook"]

def parse_response(response):
    message = response['choices'][0]['message']
    if message.get("tool_calls"):
        tool_calls = message['tool_calls'][0]
        function = tool_calls['function']
        return {
            "tool" : function['name'],
            "args" : json.loads(function['arguments']),
            "id" : tool_calls['id']
        }
    return {"answer" : message['content']}

def call_openai(messages, tools):
    for attempt in range(4):
        retry_after = None
        try:
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
            try:
                return response.json()
            except ValueError:
                logging.error("Request did not return a JSON")
        except requests.exceptions.Timeout:
            logging.warning("Request timed out, retrying...")
        except requests.exceptions.HTTPError as err:
            retry_after = err.response.headers.get('Retry-After')
            status = err.response.status_code
            if status < 500 and status != 429:
                logging.error(f"Request failed with status {status}.")
                return None
            logging.warning(f"Request failed with status {status}. Retrying...")
        except requests.exceptions.RequestException as err:
            logging.warning(f"Request failed with status {type(err).__name__}.")

        if attempt < 3:
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))
            else:
                wait = min(2 ** attempt, 20)
                time.sleep(random.uniform(0, wait))

    logging.warning(f"Request failed after 4 attempts.")
    return None

def make_brain(definitions):
    def brain(messages):
        response = call_openai(messages, definitions)
        if response is None:
            return {"answer": "Sorry, something went wrong. A human will follow up."}
        return parse_response(response)
    return brain

def classify_with_openai(question):
    messages = [
        {
            "role": "system",
            "content": 'Reply with exactly one word. Reply "orders" only if the customer names a specific order ID, or asks you to take an action on their order such as a refund or cancellation. Reply "policy" for general questions about how things work, even if they mention orders or refunds.',
        },
        {"role": "user", "content": question},
    ]
    response = call_openai(messages, [])
    if response is None:
        return "policy"
    return response["choices"][0]["message"]["content"]