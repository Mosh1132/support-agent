from idlelib import history

from support_agent.db import get_connection, seed_orders
from support_agent.agent import run_agent
from support_agent.brain import openai_brain

connection = get_connection()
seed_orders(connection)

history = []

while True:
    user = input("You: ")
    if user in ["quit", "exit"]:
        break
    print(run_agent(user, openai_brain, connection, history))