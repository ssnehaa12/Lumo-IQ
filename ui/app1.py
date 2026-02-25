import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(
    page_title="PharmEngine AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar on landing
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(135deg, #0A0E17 0%, #1a1f35 50%, #0A0E17 100%);
    }
    
    .hero-section {
        text-align: center;
        padding: 8rem 2rem 4rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    
    .hero-gradient {
        background: linear-gradient(135deg, #3B82F6 0%, #EF4444 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #8B92A8;
        margin-bottom: 3rem;
        line-height: 1.6;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .cta-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-bottom: 6rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        max-width: 1200px;
        margin: 4rem auto;
        padding: 0 2rem;
    }
    
    .feature-card {
        background: #1A1F35;
        border: 1px solid #1E2738;
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        border-color: #3B82F6;
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 0.75rem;
    }
    
    .feature-desc {
        font-size: 0.95rem;
        color: #8B92A8;
        line-height: 1.6;
    }
    
    .stats-section {
        text-align: center;
        padding: 4rem 2rem;
        background: #1A1F35;
        border-top: 1px solid #1E2738;
        border-bottom: 1px solid #1E2738;
        margin: 4rem 0;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 3rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 0.95rem;
        color: #8B92A8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">
        Enterprise Pharmacy Analytics<br>
        <span class="hero-gradient">Powered by AI</span>
    </h1>
    <p class="hero-subtitle">
        Advanced decision intelligence platform for pharmacy claims analysis. 
        Query 50,000+ claims, calculate KPIs, and generate actionable insights using natural language.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("Launch Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

st.markdown("""
<div class="stats-section">
    <div class="stats-grid">
        <div>
            <div class="stat-number">50K+</div>
            <div class="stat-label">Claims Analyzed</div>
        </div>
        <div>
            <div class="stat-number">10K+</div>
            <div class="stat-label">Member Records</div>
        </div>
        <div>
            <div class="stat-number">Real-time</div>
            <div class="stat-label">Analytics</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-title">Agentic AI</div>
        <div class="feature-desc">
            Autonomous multi-step reasoning powered by Claude. 
            Automatically queries data, generates insights, and provides recommendations.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-title">Decision Intelligence</div>
        <div class="feature-desc">
            Not just analytics - actionable recommendations with projected ROI. 
            Every insight includes next steps and business impact.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-title">Enterprise Scale</div>
        <div class="feature-desc">
            Built on Google Cloud Platform with BigQuery data warehouse. 
            Production-ready architecture designed for scale.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)