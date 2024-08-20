from uuid import uuid4

import requests
import streamlit as st

st.set_page_config(page_title="Langchain App", page_icon="🦜", layout="wide")

STARTING_MESSAGE = {
    "role": "assistant",
    "content": "Hello! How can I help you today?",
}
BACKEND_URL = "http://0.0.0.0:8686"


# Side bar
def generate_session_id():
    session_id = str(uuid4())
    st.session_state.session_id = session_id
    st.session_state.messages = [STARTING_MESSAGE]


st.sidebar.write("Session ID:")
st.sidebar.code(st.session_state.get("session_id"))
st.sidebar.button("Generate Session ID", on_click=generate_session_id)


# App title
st.title(":speaking_head_in_silhouette: Chatbot")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [STARTING_MESSAGE]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if human_input := st.chat_input():
    if not st.session_state.get("session_id"):
        st.error("Please generate a session ID first.")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": human_input})
    with st.chat_message("user"):
        st.write(human_input)
    payload = {
        "input": {
            "human_input": human_input,
        },
        "config": {"configurable": {"session_id": st.session_state.session_id}},
    }
    try:
        with st.spinner("Processing..."):
            response = requests.post(f"{BACKEND_URL}/api/v1/chat/invoke", json=payload)
            response.raise_for_status()
    except requests.exceptions.RequestException:
        st.chat_message("assistant").write(
            "Sorry, there was an unexpected error! Please try again later."
        )
        st.stop()
    else:
        message = response.json().get("output", {}).get("output", "")
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.chat_message("assistant").write(message)
