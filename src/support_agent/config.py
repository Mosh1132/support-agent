import os
from dotenv import load_dotenv
import secrets

load_dotenv()

def get_api_key():
    key = os.environ.get('LLM_API_KEY')
    if not key:
        raise RuntimeError('LLM_API_KEY is missing. Add it to your .env file.')
    return key

def get_pinecone_key():
    key = os.environ.get("PINECONE_API_KEY")
    if not key:
        raise RuntimeError('PINECONE_API_KEY is missing. Add it to your .env file.')
    return key

def check_admin_key(provided):
    expected = os.environ.get("ADMIN_KEY")
    if not expected or not provided:
        return False
    return secrets.compare_digest(provided, expected)