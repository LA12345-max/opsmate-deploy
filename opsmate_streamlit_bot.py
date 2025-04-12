
import streamlit as st
import openai
import os
import json
from datetime import datetime

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="OpsMate AI Assistant", page_icon="🤖", layout="wide")

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🤖 OpsMate AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your smart assistant for finance, sales, and support teams</p>", unsafe_allow_html=True)
st.divider()

personas = {
    "BookkeepingBot": "You are BookkeepingBot, expert in business finances, compliance, and automation.",
    "CustomerCareBot": "You are CustomerCareBot, focused on empathetic and efficient customer support.",
    "SalesBoostBot": "You are SalesBoostBot, a strategist in CRM and marketing growth."
}

MEMORY_FILE = "opsmate_streamlit_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_memory(user_id, user_msg, bot_reply):
    data = load_memory()
    if user_id not in data:
        data[user_id] = []
    data[user_id].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_msg,
        "bot": bot_reply
    })
    save_memory(data)

def get_history(user_id, max_entries=5):
    data = load_memory()
    return data.get(user_id, [])[-max_entries:]

with st.sidebar:
    st.header("🔧 Settings")
    user_id = st.text_input("User ID", value="demo_user")
    selected_persona = st.selectbox("Choose Persona", list(personas.keys()))
    show_history = st.checkbox("Show Conversation History")

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
user_input = st.text_input("💬 Ask something:", placeholder="E.g., How do I automate invoicing?", key="user_input")

if st.button("Send") and user_input.strip():
    persona_prompt = personas[selected_persona]
    history = get_history(user_id)
    chat_context = [
        {"role": "system", "content": persona_prompt}
    ]
    for entry in history:
        chat_context.append({"role": "user", "content": entry["user"]})
        chat_context.append({"role": "assistant", "content": entry["bot"]})
    chat_context.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_context,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        st.success(f"OpsMate: {reply}")
        add_memory(user_id, user_input, reply)
    except Exception as e:
        st.error(f"Error: {str(e)}")

if show_history:
    st.subheader("🕒 Past Conversations")
    full_history = get_history(user_id, 10)
    for entry in full_history:
        st.markdown(f"**🧑 You:** {entry['user']}")
        st.markdown(f"**🤖 OpsMate:** {entry['bot']}")
        st.markdown("---")

