import time
import random
import requests
import logging
from support_agent.config import get_api_key

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def split_into_chunks(text):
    chunks = []
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            chunks.append(cleaned)

    return chunks

def embed_texts(texts):
    for attempt in range(4):
        retry_after = None
        try:
            response = requests.post(
                url="https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {get_api_key()}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "text-embedding-3-small",
                    "input": texts
                },
                timeout=30
            )

            response.raise_for_status()

            try:
                return [item["embedding"] for item in response.json()['data']]
            except ValueError:
                logging.error("Request did not return a JSON")
                return None
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

