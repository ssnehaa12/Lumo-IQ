"""
PharmEngine AI - Streamlit User Interface
Professional chat interface for conversational pharmacy analytics
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.pharmacy_agent import ask_agent
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PharmEngine AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🏥 PharmEngine AI")
    st.caption("Conversational Analytics for Pharmacy Data")

st.divider()

# Sidebar
with st.sidebar:
    st.header("📊 About")
    st.markdown("""
    **PharmEngine AI** is an agentic AI system that autonomously analyzes pharmacy claims data 
    and provides actionable business insights.
    
    ### Capabilities:
    - 🔍 Query 50,000+ pharmacy claims
    - 📈 Calculate key pharmacy KPIs
    - 💡 Generate insights & recommendations
    - 🤖 Autonomous multi-step reasoning
    """)
    
    st.divider()
    
    st.header("💬 Sample Questions")
    
    sample_questions = [
        "What is our generic dispensing rate?",
        "Which drugs are driving costs?",
        "Show me specialty drug trends",
        "Identify high-risk members",
        "What's our PMPM cost?",
        "Compare Q4 2024 vs Q4 2023"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{question}", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": question,
                "timestamp": datetime.now()
            })
            st.rerun()
    
    st.divider()
    
    # Clear conversation
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.header("🛠️ Tech Stack")
    st.markdown("""
    - **LLM:** Claude Sonnet 4
    - **Framework:** LangGraph
    - **Data:** BigQuery
    - **RAG:** ChromaDB
    - **Cloud:** GCP
    """)

# Main chat interface
st.header("💬 Chat with PharmEngine AI")

# Welcome message if no conversation yet
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("""
👋 **Welcome to PharmEngine AI!**

I'm an AI agent specialized in pharmacy analytics. I can help you:
- Analyze prescription claims data
- Calculate pharmacy KPIs
- Identify cost savings opportunities
- Generate business insights and recommendations

**Try asking me a question like:**
- "What is our generic dispensing rate?"
- "Which drug categories have the highest costs?"
- "Show me specialty drug utilization trends"

Or click a sample question in the sidebar!
        """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask a question about pharmacy analytics...")

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing..."):
            try:
                # Get agent response
                response = ask_agent(user_input, verbose=False)
                st.markdown(response)
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                error_msg = f"❌ I encountered an error: {str(e)}\n\nPlease try rephrasing your question."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now()
                })

# Footer
st.divider()
st.caption("PharmEngine AI | Built with LangGraph, Claude, and BigQuery")