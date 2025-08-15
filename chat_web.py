import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import os
import json

# === Settings ===
HISTORY_FILE_TEMPLATE = "chat_history_{}.json"

# === Model Setup ===
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    model="openai/gpt-3.5-turbo",
    temperature=0
)

def load_history(username):
    filename = HISTORY_FILE_TEMPLATE.format(username)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            history = []
            for entry in data:
                if entry["role"] == "user":
                    history.append(HumanMessage(content=entry["content"]))
                elif entry["role"] == "assistant":
                    history.append(AIMessage(content=entry["content"]))
            return history
    return []

def save_history(username, history):
    filename = HISTORY_FILE_TEMPLATE.format(username)
    data = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            data.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            data.append({"role": "assistant", "content": msg.content})
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

st.set_page_config(page_title="💬 Persistent AI Chat")
st.title("💬 Persistent AI Chatbot")
st.write("Your messages are saved between sessions, but previous chats are hidden for privacy.")

if "username_confirmed" not in st.session_state:
    st.session_state.username_confirmed = False

if not st.session_state.username_confirmed:
    username_input = st.text_input("Please enter your user name:")
    if st.button("Confirm Username"):
        if username_input.strip():
            st.session_state.username = username_input.strip()
            st.session_state.username_confirmed = True

if st.session_state.get("username_confirmed", False):
    username = st.session_state.username
    if "messages" not in st.session_state:
        st.session_state.messages = load_history(username)

    st.write(f"Hello, **{username}**! Start chatting below:")

    # Previous messages hidden for privacy (only used internally)
    # for msg in st.session_state.messages:
    #     role = "user" if isinstance(msg, HumanMessage) else "assistant"
    #     st.chat_message(role).write(msg.content)

    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write(response.content)

        save_history(username, st.session_state.messages)
