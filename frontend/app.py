import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import streamlit as st
from client import GraphClient

st.set_page_config(page_title="Langchain App", page_icon="🦜", layout="wide")

STARTING_MESSAGE = {
    "type": "ai",
    "content": "Hello! How can I help you today?",
}
BACKEND_URL = "http://0.0.0.0:8686"


async def main():
    # Side bar
    with st.sidebar:

        def generate_session_id():
            session_id = str(uuid4())
            st.session_state.session_id = session_id
            st.session_state.messages = [STARTING_MESSAGE]

        st.write("Session ID:")
        st.code(st.session_state.get("session_id"))
        st.button("Generate Session ID", on_click=generate_session_id)

    # App title
    st.title(":speaking_head_in_silhouette: Chatbot")

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [STARTING_MESSAGE]

    async def amessage_iter():
        for m in st.session_state.messages:
            yield m

    await draw_message(amessage_iter())

    if human_input := st.chat_input():
        if not st.session_state.get("session_id"):
            st.error("Please generate a session ID first.")
            st.stop()

        st.session_state.messages.append({"type": "human", "content": human_input})
        st.chat_message("human").write(human_input)

        client = GraphClient(base_url=BACKEND_URL, timeout=30)
        try:
            stream = client.astream(
                message=human_input,
                thread_id=st.session_state.session_id,
            )
            await draw_message(stream, is_new=True)
        except Exception as e:
            st.session_state.messages[-1] = {
                "type": "ai",
                "content": f"An error occurred: {e}",
            }


async def draw_message(
    messages_agen: AsyncGenerator[str, None],
    is_new: bool = False,
):
    # Keep track of the last message container
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for intermediate streaming tokens
    streaming_content = ""
    streaming_placeholder = None

    # Iterate over the messages and draw them
    while msg := await anext(messages_agen, None):  # noqa: F821
        # str message represents an intermediate token being streamed
        if isinstance(msg, str):
            # If placeholder is empty, this is the first token of a new message
            # being streamed. We need to do setup.
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()

            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue
        match msg["type"]:
            case "human":
                last_message_type = "human"
                st.chat_message("human").write(msg["content"])
            case "ai":
                # If we're rendering new messages, store the message in session state
                if is_new:
                    st.session_state.messages.append(msg)

                # If the last message type was not assistant, create a new chat message
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")

                with st.session_state.last_message:
                    # If the message has content, write it out.
                    # Reset the streaming variables to prepare for the next message.
                    if msg["content"]:
                        if streaming_placeholder:
                            streaming_placeholder.write(msg["content"])
                            streaming_content = ""
                            streaming_placeholder = None
                        else:
                            st.write(msg["content"])


asyncio.run(main())
