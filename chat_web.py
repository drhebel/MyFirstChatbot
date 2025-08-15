import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
import json
import os

# === Settings ===
HISTORY_FILE = "chat_history.json"

# === Model Setup ===
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"],  # Now using Streamlit secrets
    model="openai/gpt-3.5-turbo",
    temperature=0
)

# === Load Persistent Memory ===
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            history = []
            for entry in data:
                if entry["role"] == "user":
                    history.append(HumanMessage(content=entry["content"]))
                elif entry["role"] == "assistant":
                    history.append(AIMessage(content=entry["content"]))
            return history
    return []

# === Save to Disk ===
def save_history(history):
    data = []
    for msg in history:
        if isinstance(msg, HumanMessage):
            data.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            data.append({"role": "assistant", "content": msg.content})
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Streamlit Setup ===
st.set_page_config(page_title="💬 Persistent AI Chat")
st.title("💬 Persistent AI Chatbot")
st.write("Your messages are saved between sessions.")

# === Initialize memory ===
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# === Display history ===
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    st.chat_message(role).write(msg.content)

# === Handle new input ===
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append(HumanMessage(content=prompt))
    response = llm.invoke(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))

    # Display and save
    st.chat_message("assistant").write(response.content)
    save_history(st.session_state.messages)
