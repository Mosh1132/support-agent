from support_agent.db import get_connection, seed_orders
from support_agent.agent import run_agent, build_orders_tools, build_policy_tools
from support_agent.brain import openai_brain
from support_agent.retrieval import create_pinecone_index

connection = get_connection("orders.db")
seed_orders(connection)
index = create_pinecone_index()
tools = {**build_orders_tools(connection), **build_policy_tools(index)}

history = []

while True:
    user = input("You: ")
    if user in ["quit", "exit"]:
        break
    print("Agent:", run_agent(user, openai_brain, tools, history))