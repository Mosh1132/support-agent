import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    key = os.environ.get('LLM_API_KEY')
    if not key:
        raise RuntimeError('LLM_API_KEY is missing. Add it to your .env file.')
    return key