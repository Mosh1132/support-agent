from fastapi import FastAPI
from pydantic import BaseModel
from support_agent.brain import make_brain, ORDERS_DEFINITIONS, POLICY_DEFINITIONS, classify_with_openai
from support_agent.db import get_connection, seed_orders
from support_agent.retrieval import create_pinecone_index
from support_agent.router import route_question
from support_agent.agent import build_policy_tools, build_orders_tools, run_agent

app = FastAPI()

connection = get_connection("orders.db")
seed_orders(connection)
index = create_pinecone_index()
order_brain = make_brain(ORDERS_DEFINITIONS)
policy_brain = make_brain(POLICY_DEFINITIONS)
policy_tools = build_policy_tools(index)
orders_tools = build_orders_tools(connection)
sessions = {}

class ChatRequest(BaseModel):
    session_id : str
    question : str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest):
    history = sessions.setdefault(request.session_id, [])
    label = route_question(request.question, classify_with_openai)
    if label == "orders":
        answer = run_agent(request.question, order_brain, orders_tools, history)
    else:
        answer = run_agent(request.question, policy_brain, policy_tools, history)
    return {"answer": answer}
