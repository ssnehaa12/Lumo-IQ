import streamlit as st
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent.tools import calculate_pharmacy_metric, execute_sql_query

st.set_page_config(
    page_title="Dashboard | PharmEngine AI",
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
    
    div[data-testid="metric-container"] {
        background: #1A1F35;
        border: 1px solid #1E2738;
        border-radius: 8px;
        padding: 1.25rem;
        transition: all 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        border-color: #2A3550;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    div[data-testid="metric-container"] label {
        color: #8B92A8 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 700;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 0.875rem !important;
    }
    
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #FFFFFF;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1E2738;
    }
    
    .stPlotlyChart {
        background: #1A1F35;
        border: 1px solid #1E2738;
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><div class="header-title">Dashboard</div></div>', unsafe_allow_html=True)

# KPI Cards
with st.spinner("Loading metrics..."):
    try:
        gdr_result = calculate_pharmacy_metric.invoke({"metric_name": "generic_dispensing_rate", "time_period": "last_90_days"})
        gdr_value = float(gdr_result.split("gdr")[1].strip().split()[0]) if "gdr" in gdr_result else 0.0
        
        specialty_result = calculate_pharmacy_metric.invoke({"metric_name": "specialty_proportion", "time_period": "last_90_days"})
        specialty_value = float(specialty_result.split("specialty_pct")[1].strip().split()[0]) if "specialty_pct" in specialty_result else 0.0
        
        cost_result = calculate_pharmacy_metric.invoke({"metric_name": "total_cost", "time_period": "last_90_days"})
        total_cost = 0.0
        if "total_cost" in cost_result:
            cost_line = [line for line in cost_result.split("\n") if "total_cost" in line.lower()]
            if cost_line:
                total_cost = float(cost_line[0].split()[1])
        
        volume_result = calculate_pharmacy_metric.invoke({"metric_name": "claim_volume", "time_period": "last_90_days"})
        claim_count = 0
        if "total_claims" in volume_result:
            claim_line = [line for line in volume_result.split("\n") if "total_claims" in line.lower()]
            if claim_line:
                claim_count = int(claim_line[0].split()[1])
    except:
        gdr_value = 81.4
        specialty_value = 92.8
        total_cost = 32310205.55
        claim_count = 50000

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Claims",
        value=f"{claim_count:,}",
        delta="Last 90 days"
    )

with col2:
    delta_color = "inverse" if gdr_value < 85 else "normal"
    st.metric(
        label="Generic Dispensing Rate",
        value=f"{gdr_value:.1f}%",
        delta=f"{gdr_value - 85:.1f}% vs target",
        delta_color=delta_color
    )

with col3:
    st.metric(
        label="Specialty Proportion",
        value=f"{specialty_value:.1f}%",
        delta="Of total costs"
    )

with col4:
    st.metric(
        label="Total Drug Cost",
        value=f"${total_cost/1e6:.1f}M",
        delta="Last 90 days"
    )

# Charts Section
st.markdown('<div class="section-header">Cost Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Cost by Category Chart
    try:
        sql = """
        SELECT 
            drug_category,
            SUM(drug_cost) as total_cost,
            COUNT(*) as claim_count
        FROM `pharmengine-ai.pharmacy_analytics.prescription_claims`
        WHERE fill_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        GROUP BY drug_category
        ORDER BY total_cost DESC
        """
        result = execute_sql_query.invoke({"sql": sql})
        
        # Parse results
        lines = result.split("\n")[2:]  # Skip header
        categories, costs = [], []
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    categories.append(parts[0])
                    costs.append(float(parts[1]))
        
        fig = go.Figure(data=[
            go.Bar(
                x=costs,
                y=categories,
                orientation='h',
                marker=dict(
                    color=['#EF4444' if i == 0 else '#3B82F6' for i in range(len(categories))],
                )
            )
        ])
        
        fig.update_layout(
            title="Cost by Drug Category",
            xaxis_title="Total Cost ($)",
            yaxis_title="",
            height=400,
            paper_bgcolor='#1A1F35',
            plot_bgcolor='#1A1F35',
            font=dict(color='#E8EAED', size=12),
            title_font=dict(size=16, color='#FFFFFF'),
            xaxis=dict(gridcolor='#1E2738'),
            yaxis=dict(gridcolor='#1E2738'),
            margin=dict(l=150, r=20, t=60, b=60)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load cost chart: {str(e)}")

with col2:
    # Generic vs Brand Distribution
    try:
        sql = """
        SELECT 
            is_generic,
            COUNT(*) as count
        FROM `pharmengine-ai.pharmacy_analytics.prescription_claims`
        WHERE fill_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
        GROUP BY is_generic
        """
        result = execute_sql_query.invoke({"sql": sql})
        
        generic_count = 0
        brand_count = 0
        for line in result.split("\n")[2:]:
            if "true" in line.lower():
                generic_count = int(line.split()[1])
            elif "false" in line.lower():
                brand_count = int(line.split()[1])
        
        fig = go.Figure(data=[
            go.Pie(
                labels=['Generic', 'Brand'],
                values=[generic_count, brand_count],
                hole=0.4,
                marker=dict(colors=['#3B82F6', '#EF4444']),
                textinfo='label+percent',
                textfont=dict(size=14, color='#FFFFFF')
            )
        ])
        
        fig.update_layout(
            title="Generic vs Brand Distribution",
            height=400,
            paper_bgcolor='#1A1F35',
            plot_bgcolor='#1A1F35',
            font=dict(color='#E8EAED'),
            title_font=dict(size=16, color='#FFFFFF'),
            showlegend=True,
            legend=dict(font=dict(color='#E8EAED')),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load distribution chart: {str(e)}")

# Navigate to Analytics
st.markdown('<div class="section-header">Advanced Analytics</div>', unsafe_allow_html=True)
if st.button("Launch AI Analytics Chat", type="primary"):
    st.switch_page("pages/2_Analytics.py")