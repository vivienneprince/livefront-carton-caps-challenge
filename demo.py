"""Bare-bones chat demo using Streamlit for UI."""

import logging

import streamlit as st

from utils.llms import CustomOpenAIClient
from utils.chat_agent import chat_agent


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# Initialize LLM client--OpenAI API format (see .env_template for required environment variables)
llm = CustomOpenAIClient(enable_streaming=True)

# Predefined bot greeting messages
bot_greeting = [
    "Hi! I'm Capper, your personal Carton Caps assistant.",
    "Ask me a question, and I'll do my best to help you.",
    "If there's anything I can't help you with, I'll direct you to someone who can.",
]


# Streamlit app
st.title("Chatbot Demo")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content":_} for _ in bot_greeting]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Send a message..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
        ]
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        log.info(f"User message: {prompt}")

        stream_or_str = chat_agent(query=prompt, chat_history=chat_history, llm_model=llm)
        response = st.write(stream_or_str) if isinstance(stream_or_str, str) else st.write_stream(stream_or_str)

        log.info(f"Assistant response: {response}")

    st.session_state.messages.append({"role": "assistant", "content": response})