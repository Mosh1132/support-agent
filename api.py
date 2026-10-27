from fastapi import FastAPI
from pydantic import BaseModel
from support_agent.brain import openai_brain
from support_agent.db import get_connection, seed_orders
from support_agent.retrieval import create_pinecone_index
from support_agent.agent import build_policy_tools, build_orders_tools, run_agent

app = FastAPI()

connection = get_connection("orders.db")
seed_orders(connection)
index = create_pinecone_index()
tools = {**build_orders_tools(connection), **build_policy_tools(index)}
sessions = {}

class ChatRequest(BaseModel):
    session_id : str
    question : str

@app.post("/chat")
def chat(request: ChatRequest):
    history = sessions.setdefault(request.session_id, [])
    answer = run_agent(request.question, openai_brain, tools, history)
    return {"answer": answer}