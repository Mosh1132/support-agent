import json
import time
import random
import logging
import requests
from support_agent.config import get_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def parse_response(response):
    message = response['choices'][0]['message']
    if message.get("tool_calls"):
        tool_calls = message['tool_calls']
        function = tool_calls[0]['function']
        return {"tool" : function['name'], "args" : json.loads(function['arguments'])}
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
            return response.json()
        except requests.exceptions.Timeout:
            logging.warning("Request timed out, retying...")
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
