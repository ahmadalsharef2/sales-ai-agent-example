import streamlit as st
import requests
import time
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import from app
sys.path.insert(0, str(Path(__file__).parent))
from app.utils.prompts import SYSTEM_PROMPT

# API Configuration
API_URL = "http://localhost:8000/api/chat"

# Page config
st.set_page_config(
    page_title="Bike Sales AI Agent",
    page_icon="🚴",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "total_latency" not in st.session_state:
    st.session_state.total_latency = 0
if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# Title
st.title("🚴 Bike Sales AI Agent")

# Sidebar - Prompt Editor & Stats
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # System prompt editor (using imported prompt as default)
    system_prompt = st.text_area(
        "System Prompt:",
        value=st.session_state.get("system_prompt", SYSTEM_PROMPT),
        height=200,
        help="Edit this to change the AI's behavior"
    )
    st.session_state.system_prompt = system_prompt
    
    st.markdown("---")
    
    # Session stats
    st.header("📊 Session Stats")
    st.metric("Messages Sent", st.session_state.message_count)
    
    if st.session_state.message_count > 0:
        avg_latency = st.session_state.total_latency / st.session_state.message_count
        st.metric("Avg Latency", f"{avg_latency:.3f}s")
        st.metric("Total Latency", f"{st.session_state.total_latency:.3f}s")
    
    st.markdown("---")
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.total_latency = 0
        st.session_state.message_count = 0
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Show latency for assistant messages
        if message["role"] == "assistant" and "latency" in message:
            st.caption(f"⏱️ Response time: {message['latency']:.3f}s")

# Chat input
if prompt := st.chat_input("Ask me about bikes..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            start_time = time.time()
            
            try:
                # Make API request
                response = requests.post(
                    API_URL,
                    json={
                        "message": prompt,
                        "conversation_id": st.session_state.conversation_id,
                        "system_prompt": st.session_state.system_prompt
                    },
                    timeout=30
                )
                response.raise_for_status()
                
                end_time = time.time()
                latency = end_time - start_time
                
                # Parse response
                data = response.json()
                assistant_message = data.get("response", "Sorry, I couldn't generate a response.")
                st.session_state.conversation_id = data.get("conversation_id")
                
                # Display response
                st.markdown(assistant_message)
                st.caption(f"⏱️ Response time: {latency:.3f}s")
                
                # Update stats
                st.session_state.total_latency += latency
                st.session_state.message_count += 1
                
                # Save to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "latency": latency
                })
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("❌ Request timed out. The server took too long to respond.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("💡 Tip: Edit the system prompt in the sidebar to customize the AI's behavior")
