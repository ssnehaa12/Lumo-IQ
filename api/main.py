from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from datetime import datetime, timedelta
import re
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.pharmacy_agent import ask_agent
from agent.tools import calculate_pharmacy_metric, execute_sql_query

app = FastAPI(title="PharmEngine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "https://lumo-iq.vercel.app",        # your Vercel URL (update after deploy)
        "https://*.vercel.app",               # covers all Vercel preview deployments
    ],)

# ============================================================================
# CACHING LAYER
# ============================================================================

CACHE = {
    "insights": {"data": None, "timestamp": None},
    "alerts": {"data": None, "timestamp": None},
    "benchmarks": {"data": None, "timestamp": None},
    "cohorts": {"data": None, "timestamp": None}
}

CACHE_DURATION = timedelta(hours=1)  # Cache for 1 hour

def get_cached_data(cache_key: str):
    """Return cached data if still valid"""
    cache_entry = CACHE.get(cache_key)
    if cache_entry and cache_entry["timestamp"]:
        age = datetime.now() - cache_entry["timestamp"]
        if age < CACHE_DURATION:
            print(f"✅ Returning cached {cache_key} (age: {age.seconds}s)")
            return cache_entry["data"]
    return None

def set_cached_data(cache_key: str, data: dict):
    """Store data in cache"""
    CACHE[cache_key] = {
        "data": data,
        "timestamp": datetime.now()
    }
    print(f"💾 Cached {cache_key}")

class QueryRequest(BaseModel):
    question: str

class MetricRequest(BaseModel):
    metric_name: str
    time_period: str = "last_90_days"

@app.post("/api/query")
async def query_agent(request: QueryRequest):
    """Pure agent - handles ANY natural language query"""
    try:
        print(f"\n{'='*60}")
        print(f"CHAT QUERY: {request.question}")
        print(f"{'='*60}\n")
        
        response = ask_agent(request.question, verbose=True)
        
        print(f"\n{'='*60}")
        print(f"AGENT RESPONSE: {response[:200]}...")
        print(f"{'='*60}\n")
        
        return {"response": response, "success": True}
    except Exception as e:
        print(f"ERROR in query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/metrics")
async def get_metric(request: MetricRequest):
    try:
        result = calculate_pharmacy_metric.invoke({
            "metric_name": request.metric_name,
            "time_period": request.time_period
        })
        return {"result": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sql")
async def execute_query(request: dict):
    try:
        result = execute_sql_query.invoke({"sql": request["sql"]})
        return {"result": result, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# =============================================================================
# LUMOBOARD ENDPOINTS - WITH CACHING
# =============================================================================

@app.post("/api/lumoboard/insights")
async def generate_insights():
    """Agent generates insights - CACHED"""
    try:
        # Check cache first
        cached = get_cached_data("insights")
        if cached:
            return cached
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""
        ANALYSIS TIMESTAMP: {current_time}
        
        You are a pharmacy data analyst. Query the BigQuery database RIGHT NOW using your execute_sql_query tool to generate 3 FRESH insights about the current pharmacy data.
        
        You MUST execute actual SQL queries to get real numbers. Do NOT use hypothetical or cached data.
        
        Required analyses:
        1. **Specialty Drug Analysis**: 
           - Query: Calculate what percentage of total pharmacy costs are from specialty drugs
           - Include: exact percentage, number of specialty claims, average cost per specialty claim
        
        2. **Generic Dispensing Rate**: 
           - Query: Calculate current generic dispensing rate (count of generic fills / total fills * 100)
           - Compare to 85% industry benchmark
           - Calculate potential savings if target is met
        
        3. **High-Risk Member Population**:
           - Query: Count members with risk_score >= 7
           - Calculate their total and average costs
           - Identify care management opportunities
        
        For EACH insight, provide:
        - "text": The finding with ACTUAL NUMBERS from your query results (not estimates)
        - "impact": Business impact in DOLLARS with calculations
        - "action": Specific, actionable recommendation
        - "sql": The SQL query you used (for transparency)
        
        Return response as ONLY a JSON array (no markdown, no preamble):
        [
          {{
            "text": "Specialty drugs account for X% of total costs (based on $Y total specialty spend out of $Z total spend), with N claims averaging $A per claim",
            "impact": "Consuming X% of budget, creating unsustainable cost growth. Projected annual impact: $X",
            "action": "Implement prior authorization for top 5 specialty drugs, establish preferred specialty pharmacy network, negotiate manufacturer rebates",
            "sql": "SELECT SUM(CASE WHEN drug_category='Specialty' THEN drug_cost ELSE 0 END) / SUM(drug_cost) * 100 FROM ..."
          }}
        ]
        
        Execute your SQL queries NOW and use the actual results.
        """
        
        print(f"\n{'='*80}")
        print(f"🔍 GENERATING INSIGHTS - {current_time}")
        print(f"{'='*80}\n")
        
        response = ask_agent(prompt, verbose=True)
        
        print(f"\n{'='*80}")
        print(f"📊 INSIGHTS AGENT RESPONSE:")
        print(response[:500] + "..." if len(response) > 500 else response)
        print(f"{'='*80}\n")
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            insights = json.loads(json_match.group(0))
            print(f"✅ Successfully parsed {len(insights)} insights\n")
            result = {"insights": insights, "success": True, "cached": False}
            
            # Cache it
            set_cached_data("insights", result)
            
            return result
        else:
            print("⚠️ Could not parse JSON from agent response\n")
            return {
                "insights": [{
                    "text": "Analysis in progress - agent response could not be parsed",
                    "impact": "Refresh page to retry",
                    "action": "Wait a moment and reload",
                    "sql": ""
                }],
                "success": True,
                "cached": False
            }
    except Exception as e:
        print(f"❌ ERROR in insights: {str(e)}\n")
        return {"insights": [], "success": False, "error": str(e)}

@app.post("/api/lumoboard/alerts")
async def check_alerts():
    """Agent identifies alerts - CACHED"""
    try:
        # Check cache first
        cached = get_cached_data("alerts")
        if cached:
            return cached
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""
        ALERT CHECK TIMESTAMP: {current_time}
        
        You are a pharmacy operations monitor. Query the database RIGHT NOW using your execute_sql_query tool to check for metric violations.
        
        Check these thresholds by executing SQL queries:
        
        1. **Generic Dispensing Rate (GDR)**:
           - Query: Calculate (COUNT of generic fills / COUNT of total fills * 100)
           - Threshold: Should be >= 85%
           - If below: Create WARNING alert
        
        2. **Specialty Cost Share**:
           - Query: Calculate (SUM of specialty drug costs / SUM of total drug costs * 100)
           - Threshold: Should be <= 50%
           - If above: Create HIGH alert
        
        For any metric violating thresholds, return alert details with ACTUAL QUERIED VALUES.
        
        Return ONLY a JSON array (no markdown, no preamble):
        [
          {{
            "severity": "warning",
            "metric": "Generic Dispensing Rate",
            "current": 81.7,
            "threshold": 85.0,
            "message": "GDR at 81.7% is 3.3 percentage points below target threshold of 85%",
            "impact": "Potential annual savings of $980K if GDR reaches 85% target. Each 1% increase saves approximately $300K annually.",
            "sql": "SELECT COUNT(CASE WHEN is_generic THEN 1 END) * 100.0 / COUNT(*) FROM ..."
          }}
        ]
        
        If ALL metrics are within acceptable ranges, return empty array: []
        
        Execute SQL queries NOW and use actual current values.
        """
        
        print(f"\n{'='*80}")
        print(f"⚠️  CHECKING ALERTS - {current_time}")
        print(f"{'='*80}\n")
        
        response = ask_agent(prompt, verbose=True)
        
        print(f"\n{'='*80}")
        print(f"🚨 ALERTS AGENT RESPONSE:")
        print(response[:500] + "..." if len(response) > 500 else response)
        print(f"{'='*80}\n")
        
        # Extract JSON
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            alerts = json.loads(json_match.group(0))
            print(f"✅ Found {len(alerts)} alerts\n")
            result = {"alerts": alerts, "success": True, "cached": False}
            
            # Cache it
            set_cached_data("alerts", result)
            
            return result
        else:
            print("⚠️ Could not parse JSON, assuming no alerts\n")
            result = {"alerts": [], "success": True, "cached": False}
            set_cached_data("alerts", result)
            return result
    except Exception as e:
        print(f"❌ ERROR in alerts: {str(e)}\n")
        return {"alerts": [], "success": False, "error": str(e)}

@app.post("/api/lumoboard/benchmarks")
async def get_benchmarks():
    """Agent compares metrics - CACHED"""
    try:
        # Check cache first
        cached = get_cached_data("benchmarks")
        if cached:
            return cached
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""
        BENCHMARK ANALYSIS TIMESTAMP: {current_time}
        
        You are a healthcare analytics consultant. Query the database RIGHT NOW using your execute_sql_query tool to compare our performance against industry benchmarks.
        
        Execute these queries to get OUR ACTUAL current values:
        
        1. **Generic Dispensing Rate**:
           - Query: (COUNT of generic fills / COUNT of total fills * 100)
           - Industry benchmark: 85%
        
        2. **Specialty Cost Share**:
           - Query: (SUM of specialty costs / SUM of total costs * 100)
           - Industry benchmark: 50%
        
        3. **PMPM Cost** (Per Member Per Month):
           - Query: (SUM of total drug costs / COUNT of distinct members / 3)  [assuming 90-day period = 3 months]
           - Industry benchmark: $300
        
        For each metric, calculate the gap and determine status.
        
        Return ONLY a JSON array (no markdown, no preamble):
        [
          {{
            "metric": "Generic Dispensing Rate",
            "your_value": 81.7,
            "industry_avg": 85.0,
            "gap": -3.3,
            "status": "below",
            "sql": "SELECT COUNT(CASE WHEN is_generic THEN 1 END) * 100.0 / COUNT(*) FROM ..."
          }}
        ]
        
        Execute SQL queries NOW to get current values.
        """
        
        print(f"\n{'='*80}")
        print(f"📊 GENERATING BENCHMARKS - {current_time}")
        print(f"{'='*80}\n")
        
        response = ask_agent(prompt, verbose=True)
        
        print(f"\n{'='*80}")
        print(f"📈 BENCHMARKS AGENT RESPONSE:")
        print(response[:500] + "..." if len(response) > 500 else response)
        print(f"{'='*80}\n")
        
        # Extract JSON
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            benchmarks = json.loads(json_match.group(0))
            print(f"✅ Generated {len(benchmarks)} benchmark comparisons\n")
            result = {"benchmarks": benchmarks, "success": True, "cached": False}
            
            # Cache it
            set_cached_data("benchmarks", result)
            
            return result
        else:
            print("⚠️ Could not parse JSON\n")
            result = {"benchmarks": [], "success": True, "cached": False}
            set_cached_data("benchmarks", result)
            return result
    except Exception as e:
        print(f"❌ ERROR in benchmarks: {str(e)}\n")
        return {"benchmarks": [], "success": False, "error": str(e)}

@app.post("/api/lumoboard/cohorts")
async def analyze_cohorts(request: dict = {}):
    """Agent performs cohort analysis - CACHED"""
    try:
        # Check cache first
        cached = get_cached_data("cohorts")
        if cached:
            return cached
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        segment_by = request.get('segment_by', 'plan_type') if request else 'plan_type'
        
        prompt = f"""
        COHORT ANALYSIS TIMESTAMP: {current_time}
        
        You are a population health analyst. Query the database RIGHT NOW using your execute_sql_query tool to perform cohort segmentation analysis.
        
        Segment the member population by: {segment_by}
        
        Execute this SQL query:
        - Join member_demographics and prescription_claims tables
        - GROUP BY {segment_by}
        - For each segment, calculate:
          * COUNT(DISTINCT member_id) as member_count
          * AVG(drug_cost) as avg_cost
        - ORDER BY avg_cost DESC (highest cost segments first)
        - Filter to last 90 days
        
        Return ONLY a JSON array (no markdown, no preamble):
        [
          {{
            "segment": "Medicare",
            "member_count": 3027,
            "avg_cost": 655.89,
            "sql": "SELECT plan_type, COUNT(DISTINCT m.member_id), AVG(c.drug_cost) FROM ..."
          }}
        ]
        
        Execute SQL query NOW and use actual results. Order by avg_cost descending.
        """
        
        print(f"\n{'='*80}")
        print(f"👥 PERFORMING COHORT ANALYSIS - {current_time}")
        print(f"   Segmenting by: {segment_by}")
        print(f"{'='*80}\n")
        
        response = ask_agent(prompt, verbose=True)
        
        print(f"\n{'='*80}")
        print(f"📊 COHORTS AGENT RESPONSE:")
        print(response[:500] + "..." if len(response) > 500 else response)
        print(f"{'='*80}\n")
        
        # Extract JSON
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            cohorts = json.loads(json_match.group(0))
            print(f"✅ Identified {len(cohorts)} cohorts\n")
            result = {"cohorts": cohorts, "success": True, "cached": False}
            
            # Cache it
            set_cached_data("cohorts", result)
            
            return result
        else:
            print("⚠️ Could not parse JSON\n")
            result = {"cohorts": [], "success": True, "cached": False}
            set_cached_data("cohorts", result)
            return result
    except Exception as e:
        print(f"❌ ERROR in cohorts: {str(e)}\n")
        return {"cohorts": [], "success": False, "error": str(e)}

# Clear cache endpoint (for testing)
@app.post("/api/lumoboard/clear-cache")
async def clear_cache():
    """Clear all cached data"""
    global CACHE
    CACHE = {
        "insights": {"data": None, "timestamp": None},
        "alerts": {"data": None, "timestamp": None},
        "benchmarks": {"data": None, "timestamp": None},
        "cohorts": {"data": None, "timestamp": None}
    }
    return {"message": "Cache cleared", "success": True}

# =============================================================================
# MY BOARD ENDPOINT
# =============================================================================

@app.post("/api/myboard/generate-widget")
async def generate_custom_widget(request: dict):
    """Agent handles ANY user query and returns appropriate widget format"""
    try:
        user_query = request.get('query', '')
        query_lower = user_query.lower()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*80}")
        print(f"🎯 CUSTOM WIDGET REQUEST - {current_time}")
        print(f"   Query: {user_query}")
        print(f"{'='*80}\n")
        
        # Detect widget type from query
        is_comparison = ' vs ' in query_lower or 'compare' in query_lower
        is_list = any(x in query_lower for x in ['top ', 'highest', 'lowest', 'which ', '3 ', '5 ', '10 '])
        is_percentage = '%' in query_lower or 'percentage' in query_lower or 'percent' in query_lower
        
        if is_comparison:
            prompt = f"""
            TIMESTAMP: {current_time}
            
            Answer this comparison query using your execute_sql_query tool: "{user_query}"
            
            Execute SQL queries to get ACTUAL data for both categories being compared.
            
            Return ONLY a JSON object (no markdown, no preamble):
            {{
              "left_label": "Category 1 name",
              "left_value": "$X.XM or $X.XK",
              "right_label": "Category 2 name", 
              "right_value": "$X.XM or $X.XK",
              "sql": "The SQL query you used to get this data"
            }}
            
            IMPORTANT: Include the actual SQL you executed in the "sql" field.
            """
            
            print("   Type: COMPARISON\n")
            response = ask_agent(prompt, verbose=True)
            
            print(f"\n   Response preview: {response[:200]}...\n")
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "widget": {
                        "id": str(datetime.now().timestamp()),
                        "type": "comparison",
                        "title": user_query[:50],
                        "left_label": data["left_label"],
                        "left_value": data["left_value"],
                        "right_label": data["right_label"],
                        "right_value": data["right_value"],
                        "sql": data.get("sql", ""),
                        "query": user_query,
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        elif is_list:
            prompt = f"""
            TIMESTAMP: {current_time}
            
            Answer this query using your execute_sql_query tool: "{user_query}"
            
            Execute SQL query to get ranked list with ACTUAL data.
            
            Return ONLY a JSON object (no markdown, no preamble):
            {{
              "items": [
                {{"name": "Item 1", "value": "$XXX.XX or count"}},
                {{"name": "Item 2", "value": "$XXX.XX or count"}}
              ],
              "sql": "The SQL query you used"
            }}
            
            IMPORTANT: Include the actual SQL you executed in the "sql" field.
            """
            
            print("   Type: LIST\n")
            response = ask_agent(prompt, verbose=True)
            
            print(f"\n   Response preview: {response[:200]}...\n")
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "widget": {
                        "id": str(datetime.now().timestamp()),
                        "type": "list",
                        "title": user_query[:50],
                        "items": data["items"],
                        "sql": data.get("sql", ""),
                        "query": user_query,
                        "timestamp": datetime.now().isoformat()
                    }
                }
        
        else:
            # Single KPI
            if is_percentage:
                prompt = f"""
                TIMESTAMP: {current_time}
                
                Answer this question using your execute_sql_query tool: "{user_query}"
                
                Your response MUST include a PERCENTAGE value (e.g., "45.2%").
                Do NOT return a dollar amount.
                
                After executing your SQL query, provide TWO things:
                1. The answer in ONE sentence
                2. The SQL query you used
                
                Format:
                Answer: [Your one-sentence answer]
                SQL: [The exact SQL you executed]
                """
            else:
                prompt = f"""
                TIMESTAMP: {current_time}
                
                Answer this question using your execute_sql_query tool: "{user_query}"
                
                Execute SQL query NOW and provide TWO things:
                1. A concise answer in ONE sentence with the numeric value
                2. The SQL query you used
                
                Format:
                Answer: [Your answer]
                SQL: [The exact SQL you executed]
                
                Examples:
                Answer: The average cost is $234.56
                SQL: SELECT AVG(drug_cost) FROM prescription_claims WHERE...
                """
            
            print("   Type: SINGLE KPI\n")
            response = ask_agent(prompt, verbose=True)
            
            print(f"\n   Response: {response}\n")
            
            # Extract SQL
            sql_match = re.search(r'SQL:\s*(.+?)(?:\n|$)', response, re.IGNORECASE | re.DOTALL)
            sql_query = sql_match.group(1).strip() if sql_match else ""
            
            # Extract value from response
            if is_percentage:
                pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', response)
                if pct_match:
                    display_value = f"{pct_match.group(1)}%"
                else:
                    display_value = "N/A"
            else:
                currency_match = re.search(r'\$[\d,]+(?:\.\d+)?[KMB]?', response)
                if currency_match:
                    display_value = currency_match.group(0)
                else:
                    pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', response)
                    if pct_match:
                        display_value = f"{pct_match.group(1)}%"
                    else:
                        num_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', response)
                        if num_match:
                            display_value = num_match.group(1)
                        else:
                            display_value = "N/A"
            
            title = ' '.join(user_query.split()[:8]).title()
            if len(title) > 50:
                title = title[:47] + "..."
            
            return {
                "success": True,
                "widget": {
                    "id": str(datetime.now().timestamp()),
                    "type": "single",
                    "title": title,
                    "value": display_value,
                    "sql": sql_query,
                    "query": user_query,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
    except Exception as e:
        print(f"❌ ERROR in generate_widget: {str(e)}\n")
        return {"success": False, "error": str(e)}
    
@app.post("/api/analysis/metrics")
async def get_analysis_metrics(request: dict):
    """Agent generates analysis metrics based on template and time period - FULLY AGENTIC"""
    try:
        template = request.get('template', 'executive')
        days = request.get('days', 90)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Define what each template should focus on
        template_focus = {
            "executive": "business performance, total costs, volume, efficiency, PMPM",
            "clinical": "clinical quality, adherence, risk scores, generic usage, mail order, member health",
            "financial": "cost drivers, savings opportunities, specialty spend, generic opportunities, PMPM costs"
        }
        
        focus = template_focus.get(template, "overall pharmacy performance")
        
        prompt = f"""
        TIMESTAMP: {current_time}
        
        You are a pharmacy analytics consultant. Generate 6 KEY METRICS for a {template.upper()} dashboard.
        
        IMPORTANT: Query the database for the LAST {days} DAYS and compare with the PREVIOUS {days} DAYS.
        
        Focus area for {template}: {focus}
        
        For EACH metric:
        1. Use execute_sql_query to get CURRENT period data (last {days} days)
        2. Use execute_sql_query to get PREVIOUS period data (previous {days} days before that)
        3. Calculate the change (current vs previous)
        4. Determine trend direction (up/down/neutral)
        5. Assign appropriate status and status type
        
        Return ONLY a JSON array with 3 metrics:
        [
          {{
            "title": "Metric name",
            "status": "Status label (e.g., Elevated, Optimal, Below Target)",
            "statusType": "low|moderate|high|critical",
            "description": "Detailed description with actual numbers from your query",
            "value": numeric_value_for_visualization,
            "displayType": "progress|score|ring",
            "change": "Comparison vs previous period (e.g., +8.2% vs previous period, +124 vs previous period)",
            "trend": "up|down|neutral"
          }}
        ]
        
        METRICS TO INCLUDE BASED ON TEMPLATE:

**If template = "executive":**
1. Total Pharmacy Spend (last {days} days vs previous {days} days)
2. Generic Dispensing Rate (current vs previous period)
3. PMPM Cost (current vs previous)

**If template = "clinical":**
1. High-Risk Members (risk_score > 2.0)
2. Generic Dispensing Rate
3. Average Risk Score

**If template = "financial":**
1. Total Pharmacy Spend
2. Specialty Drug Share
3. Generic Savings Opportunity
        
        DISPLAY TYPE RULES:
- Use "progress" for percentages with progress bars (e.g., GDR at 81.7%)
- Use "ring" for percentages shown in circles (e.g., utilization rates)
- Use "score" ONLY for dollar amounts or counts (DO NOT use /10 format)

When using "score" type:
- The value should be the actual number (e.g., 328.5 for $328.50 PMPM)
- The description should include the formatted display (e.g., "$328.46")
- Do NOT format as "X/10"

DO NOT include more than 3 metrics. Only return 3.

        
        Execute all SQL queries NOW using the last {days} days and previous {days} days for comparison.
        Return ONLY the JSON array, no preamble.
        """
        
        print(f"\n{'='*80}")
        print(f"📊 GENERATING {template.upper()} METRICS - Last {days} days")
        print(f"{'='*80}\n")
        
        response = ask_agent(prompt, verbose=True)
        
        print(f"\n{'='*80}")
        print(f"📈 METRICS AGENT RESPONSE:")
        print(response[:800] + "..." if len(response) > 800 else response)
        print(f"{'='*80}\n")
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            metrics = json.loads(json_match.group(0))
            print(f"✅ Successfully generated {len(metrics)} metrics for {template}\n")
            return {"metrics": metrics, "success": True}
        else:
            print("⚠️ Could not parse JSON from agent response\n")
            # Fallback metrics
            return {
                "metrics": [{
                    "title": "Data Loading",
                    "status": "Processing",
                    "statusType": "moderate",
                    "description": f"Generating {template} metrics for last {days} days...",
                    "value": 50,
                    "displayType": "progress",
                    "change": "Calculating...",
                    "trend": "neutral"
                }],
                "success": True
            }
    except Exception as e:
        print(f"❌ ERROR in analysis metrics: {str(e)}\n")
        return {"metrics": [], "success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)