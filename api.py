from fastapi import FastAPI
from pydantic import BaseModel
from support_agent.brain import make_brain, ORDERS_DEFINITIONS, POLICY_DEFINITIONS, classify_with_openai
from support_agent.db import get_connection, seed_orders
from support_agent.retrieval import create_pinecone_index
from support_agent.router import route_question
from support_agent.agent import build_policy_tools, build_orders_tools, run_agent
from fastapi import FastAPI, Header, HTTPException
from support_agent.approvals import decide_approval, list_pending_approvals
from support_agent.config import check_admin_key

def require_admin(x_admin_key):
    if not check_admin_key(x_admin_key):
        raise HTTPException(status_code=401, detail="Invalid admin key")
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

@app.get("/approvals")
def get_approvals(x_admin_key: str = Header(None)):
    require_admin(x_admin_key)
    return list_pending_approvals(connection)

@app.post("/approvals/{approval_id}/approve")
def approve(approval_id: int, x_admin_key: str = Header(None)):
    require_admin(x_admin_key)
    return decide_approval(approval_id, "approved", connection)


@app.post("/approvals/{approval_id}/reject")
def reject(approval_id: int, x_admin_key: str = Header(None)):
    require_admin(x_admin_key)
    return decide_approval(approval_id, "rejected", connection)
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
