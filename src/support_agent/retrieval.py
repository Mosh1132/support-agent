import time
import random
import requests
import logging
from pinecone import Pinecone, ServerlessSpec
from support_agent.config import get_api_key, get_pinecone_key

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

def create_pinecone_index(index_name='handbook'):
    pc = Pinecone(api_key=get_pinecone_key())
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)
    index = pc.Index(index_name)
    return index

def ingest_handbook(path, index):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    chunks = split_into_chunks(text)
    embeddings = embed_texts(chunks)
    if embeddings is None:
        logging.error("Embedder not working")
        return None
    records = [
        {
            'id': f"policy_{x}",
            "values": embeddings[x],
            "metadata": {"text": chunks[x]}
        } for x in range(len(embeddings))
    ]

    index.upsert(
        vectors=records
    )

def search_handbook(question, index, top_k=3):
    response = index.query(
        vector=embed_texts(question)[0],
        top_k=top_k,
        include_metadata=True
    )
    return [policy.metadata['text'] for policy in response.matches]