import uuid
import requests
import streamlit as st

st.title("Support agent")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input("Ask about an order or a policy")
if question:
    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={"session_id": st.session_state.session_id, "question": question},
        timeout=60,
    )
    answer = response.json()["answer"]
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
