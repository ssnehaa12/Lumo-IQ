"""
PharmEngine AI Agent
Agentic AI system for pharmacy analytics using LangGraph
"""

import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from agent.tools import (
    execute_sql_query,
    get_table_schema,
    calculate_pharmacy_metric
)
from agent.rag_system import DocumentationRAG
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GCP_PROJECT_ID')

print("🤖 Initializing PharmEngine AI Agent...")

# Initialize Claude
llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    temperature=0.1,
    max_tokens=4096
)

# Initialize RAG system
print("📚 Loading documentation system...")
rag = DocumentationRAG()

# ============================================
# CREATE RAG TOOL FOR AGENT
# ============================================

@tool
def search_documentation(query: str) -> str:
    """
    Search pharmacy business documentation for definitions, KPIs, best practices, and examples.
    
    Use this tool when you need to understand:
    - Business terminology (e.g., "What is generic dispensing rate?")
    - How to calculate metrics (e.g., "How to calculate PMPM?")
    - Industry context and benchmarks
    - Query examples for specific analyses
    
    Args:
        query: Your question about pharmacy business concepts
        
    Returns:
        Relevant documentation context
    """
    return rag.search(query, k=2)

# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """You are PharmEngine AI, an expert pharmacy analytics assistant powered by agentic AI.

**Your Capabilities:**
- Query BigQuery pharmacy claims data autonomously
- Search business documentation for context
- Calculate pharmacy KPIs and metrics
- Generate insights and actionable recommendations
- Reason through complex multi-step analytical problems

**Available Data:**
1. **prescription_claims** - 50,000+ pharmacy claims (2023-present)
   - Contains: claim_id, fill_date, member_id, drug_name, drug_category, is_generic, tier, quantity, days_supply, drug_cost, copay, pharmacy_id, pharmacy_type

2. **member_demographics** - 10,000+ member records
   - Contains: member_id, age, gender, state, plan_type, chronic_conditions, risk_score

3. **drug_formulary** - Formulary tier and management information
   - Contains: drug_name, drug_category, tier, is_generic, prior_auth_required, step_therapy_required, preferred_alternative, awp_cost

**Your Approach:**
1. **Understand the Question**: Break down what the user is asking
2. **Plan Your Analysis**: Determine what data and calculations you need
3. **Execute**: Use tools to gather information
   - Use `search_documentation` for business context and definitions
   - Use `get_table_schema` to understand table structures
   - Use `execute_sql_query` for custom data queries
   - Use `calculate_pharmacy_metric` for standard KPIs
4. **Analyze**: Interpret the results in business context
5. **Recommend**: Provide actionable insights with expected impact

**Important Guidelines:**
- Always use fully qualified table names: `pharmengine-ai.pharmacy_analytics.table_name`
- When writing SQL, add appropriate filters (dates, limits) to keep queries efficient
- Provide business context, not just raw numbers (e.g., "GDR is 81.4%, which is below the 85% industry target")
- If a metric looks unusual, investigate root causes
- Always include actionable recommendations when appropriate
- Format currency as USD with $ symbol
- Use clear, concise language suitable for business stakeholders

**Response Format:**
- Start with a direct answer to the question
- Provide supporting data/analysis
- End with insights and recommendations (if applicable)
- Use markdown formatting for readability

**Example Interaction:**
User: "What's our generic dispensing rate?"
You: 
1. Search documentation to understand GDR
2. Calculate GDR metric
3. Respond: "Your Generic Dispensing Rate (GDR) is 81.4% for the last 90 days. This is below the industry target of 85%, representing an opportunity for cost savings. Every 1% increase in GDR saves approximately $300K annually. 

Recommendations:
- Review brand drugs with available generic alternatives
- Implement lower copays for generic medications
- Educate prescribers on generic equivalence"

You are analytical, insightful, and action-oriented. Let's help drive better pharmacy outcomes!
"""

# ============================================
# CREATE AGENT
# ============================================

# Combine all tools
tools = [
    execute_sql_query,
    get_table_schema,
    calculate_pharmacy_metric,
    search_documentation
]

# Create the agent with system prompt in messages
agent = create_react_agent(
    llm,
    tools=tools
)

print("✓ Agent initialized with 4 tools")
print("  - execute_sql_query")
print("  - get_table_schema")
print("  - calculate_pharmacy_metric")
print("  - search_documentation")
print()

# ============================================
# HELPER FUNCTION
# ============================================

def ask_agent(question: str, verbose: bool = True) -> str:
    """
    Ask the PharmEngine AI agent a question
    
    Args:
        question: Your pharmacy analytics question
        verbose: If True, print agent's reasoning steps
        
    Returns:
        Agent's response
    """
    
    if verbose:
        print("="*70)
        print(f"❓ Question: {question}")
        print("="*70)
        print()
    
    # Create messages with system prompt
    messages = [
        ("system", SYSTEM_PROMPT),
        ("user", question)
    ]
    
    # Invoke agent
    response = agent.invoke(
        {"messages": messages},
        config={"recursion_limit": 50}
    )
    
    # Extract final response
    final_response = response["messages"][-1].content
    
    if verbose:
        print("\n" + "="*70)
        print("💡 Answer:")
        print("="*70)
        print(final_response)
        print()
    
    return final_response

# ============================================
# TEST THE AGENT
# ============================================

if __name__ == "__main__":
    print("🧪 Testing PharmEngine AI Agent")
    print("="*70)
    print()
    
    # Test questions
    test_questions = [
        "What is our generic dispensing rate?",
        "How many total claims do we have?",
        "Which drug categories have the highest costs?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"Test {i}/{len(test_questions)}")
        print(f"{'='*70}\n")
        
        try:
            ask_agent(question, verbose=True)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < len(test_questions):
            print("\n" + "-"*70)
            input("Press Enter to continue to next test...")
    
    print("\n" + "="*70)
    print("✅ Agent Testing Complete!")
    print("="*70)