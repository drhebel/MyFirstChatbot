import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import os
import json

# === Model Setup ===
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    model="openai/gpt-3.5-turbo",
    temperature=0,
)

# === Helpers ===
def get_history_file(username):
    return f"chat_history_{username}.json"

def load_history(username):
    path = get_history_file(username)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
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
    path = get_history_file(username)
    data = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            data.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            data.append({"role": "assistant", "content": msg.content})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Streamlit UI ===
st.set_page_config(page_title="💬 Streamlit Chatbot with Memory")
st.title("💬 Persistent Chatbot with Per-Session Display")

# === Username Logic ===
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.username:
    st.session_state.username = st.text_input("Enter your username to begin:")

if st.session_state.username:
    # Initialize in-session messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.write(f"👤 Logged in as: {st.session_state.username}")
    st.write("Start chatting below. Only **this session's** messages are shown. Memory is saved per user.")

    # === Chat Display: Show current session messages ===
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.write(msg.content)

    # === Chat Input ===
    if prompt := st.chat_input("Say something..."):
        # Append user message
        user_msg = HumanMessage(content=prompt)
        st.session_state.messages.append(user_msg)

        # Load full history (including past sessions)
        full_history = load_history(st.session_state.username)
        full_history += [user_msg]

        # Get model response
        response = llm.invoke(full_history)
        assistant_msg = AIMessage(content=response.content)

        # Append assistant message to session state and history
        st.session_state.messages.append(assistant_msg)
        full_history.append(assistant_msg)

        # Save updated full history (persistent memory)
        save_history(st.session_state.username, full_history)

        # Show assistant response
        with st.chat_message("assistant"):
            st.write(response.content)
