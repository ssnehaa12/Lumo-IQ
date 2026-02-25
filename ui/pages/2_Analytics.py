import streamlit as st
import sys
import os
from datetime import datetime
import plotly.graph_objects as go
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent.pharmacy_agent import ask_agent

st.set_page_config(
    page_title="Analytics | PharmEngine AI",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0A0E17;
    }
    
    [data-testid="stSidebar"] {
        background: #0F1320;
        border-right: 1px solid #1E2738;
    }
    
    .main-header {
        background: #1A1F35;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #1E2738;
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    
    .stChatMessage {
        background: #1A1F35 !important;
        border: 1px solid #1E2738 !important;
        border-radius: 8px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: #0F1320 !important;
        border-left: 3px solid #3B82F6 !important;
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: #1A1F35 !important;
        border-left: 3px solid #FFFFFF !important;
    }
    
    .stChatInput > div {
        background: #1A1F35;
        border: 1px solid #2A3550;
        border-radius: 8px;
    }
    
    .stChatInput input {
        color: #FFFFFF;
    }
    
    .stButton > button {
        background: #1A1F35;
        color: #FFFFFF;
        border: 1px solid #2A3550;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #2A3550;
        border-color: #3B82F6;
    }
    
    .query-meta {
        background: #0F1320;
        border: 1px solid #1E2738;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-top: 1rem;
        font-size: 0.875rem;
        color: #8B92A8;
        font-family: 'Monaco', monospace;
    }
    
    .insight-card {
        background: #0F1320;
        border-left: 3px solid #3B82F6;
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .insight-title {
        color: #3B82F6;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .warning-card {
        background: rgba(239, 68, 68, 0.1);
        border-left: 3px solid #EF4444;
        border-radius: 6px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-title {
        color: #EF4444;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    table {
        background: #0F1320;
        border: 1px solid #1E2738;
        border-radius: 6px;
        width: 100%;
        margin: 1rem 0;
    }
    
    th {
        background: #1A1F35;
        color: #8B92A8;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.75rem 1rem;
        text-align: left;
    }
    
    td {
        color: #E8EAED;
        padding: 0.75rem 1rem;
        border-top: 1px solid #1E2738;
    }
    
    code {
        background: #0F1320;
        color: #8B92A8;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.875rem;
        border: 1px solid #1E2738;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

st.markdown('<div class="main-header"><div class="header-title">AI Analytics</div></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Quick Queries")
    
    queries = [
        "What is our generic dispensing rate?",
        "Which drugs are driving costs?",
        "Show me specialty drug trends",
        "Identify high-risk members",
        "Calculate PMPM cost",
        "Compare Q4 2024 vs Q4 2023"
    ]
    
    for query in queries:
        if st.button(query, key=f"q_{query}", use_container_width=True):
            st.session_state.messages.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now()
            })
            st.rerun()
    
    st.divider()
    
    st.markdown(f"**Queries:** {st.session_state.query_count}")
    
    if st.button("Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.rerun()
    
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

# Welcome message
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; color: #5A617A;">
        <div style="font-size: 1.25rem; font-weight: 600; color: #FFFFFF; margin-bottom: 1rem;">
            AI-Powered Analytics
        </div>
        <div style="font-size: 0.95rem; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            Ask complex questions about pharmacy claims data. The AI agent will autonomously 
            query BigQuery, analyze results, and generate actionable insights with business impact.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        
        if message["role"] == "assistant":
            # Parse tables from response
            if "|" in content and "---" in content:
                parts = content.split("|")
                if len(parts) > 2:
                    # Has table, display nicely
                    st.markdown(content)
            else:
                st.markdown(content)
        else:
            st.markdown(content)

# Chat input
if prompt := st.chat_input("Ask a question about pharmacy analytics..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now()
    })
    st.session_state.query_count += 1
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = ask_agent(prompt, verbose=False)
                
                # Enhanced formatting
                formatted_response = response
                
                # Detect warnings (GDR below target, etc)
                if "below" in response.lower() and "target" in response.lower():
                    formatted_response = formatted_response.replace(
                        "below the industry target", 
                        '<div class="warning-card"><div class="warning-title">Below Target</div>Performance is below industry benchmark</div>'
                    )
                
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
            except Exception as e:
                error_msg = "Analysis failed. Please try rephrasing your query."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now()
                })