
import streamlit as st
import openai
import os
import json
from datetime import datetime

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="OpsMate AI", page_icon="🤖")
st.title("🤖 OpsMate AI Assistant")

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

user_id = st.text_input("Enter your user ID", "demo_user")
selected_persona = st.selectbox("Select a persona", list(personas.keys()))
user_input = st.text_input("Ask OpsMate something:")

if st.button("Send") and user_input.strip():
    persona_prompt = personas[selected_persona]
    history = get_history(user_id)
    context = "\n".join([f"User: {m['user']}\nOpsMate: {m['bot']}" for m in history])
    full_prompt = f"""{persona_prompt}
{context}
User: {user_input}
OpsMate:"""

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=full_prompt,
            max_tokens=300,
            temperature=0.7
        )
        reply = response.choices[0].text.strip()
        st.success(f"OpsMate: {reply}")
        add_memory(user_id, user_input, reply)
    except Exception as e:
        st.error(f"Error: {str(e)}")

if st.checkbox("Show past conversation"):
    history = get_history(user_id, 10)
    for entry in history:
        st.markdown(f"**You:** {entry['user']}")
        st.markdown(f"**OpsMate:** {entry['bot']}")
        st.markdown("---")
