"""
Tools for PharmEngine AI Agent
Provides capabilities to query BigQuery, search documentation, and analyze data
"""

from langchain_core.tools import tool
from google.cloud import bigquery
import os
from dotenv import load_dotenv
import pandas as pd
from typing import Optional

load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
DATASET_ID = os.getenv('BIGQUERY_DATASET')

# Initialize BigQuery client
bq_client = bigquery.Client(project=PROJECT_ID)

# ============================================
# TOOL 1: BigQuery SQL Executor
# ============================================

@tool
def execute_sql_query(sql: str) -> str:
    """
    Execute a SQL query on BigQuery and return results.
    
    Use this tool to query pharmacy claims data, member demographics, or formulary information.
    
    Args:
        sql: A valid BigQuery SQL query (SELECT statements only)
        
    Returns:
        Query results formatted as a string, or error message
        
    Example queries:
    - "SELECT COUNT(*) as total_claims FROM `pharmengine-ai.pharmacy_analytics.prescription_claims`"
    - "SELECT drug_category, SUM(drug_cost) as total_cost FROM `pharmengine-ai.pharmacy_analytics.prescription_claims` GROUP BY 1"
    
    IMPORTANT: 
    - Always use fully qualified table names: `project.dataset.table`
    - Only SELECT queries are allowed (no INSERT, UPDATE, DELETE, DROP)
    - Add LIMIT clause for large result sets
    """
    
    try:
        # Security check: only allow SELECT queries
        sql_upper = sql.strip().upper()
        dangerous_keywords = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE']
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return f"❌ Error: {keyword} statements are not allowed. Only SELECT queries permitted."
        
        # Check if LIMIT is present for safety
        if 'LIMIT' not in sql_upper and 'COUNT' not in sql_upper:
            # Add LIMIT if not present (prevent huge result sets)
            sql = sql.rstrip(';') + ' LIMIT 100'
        
        # Execute query
        query_job = bq_client.query(sql)
        results = query_job.result()
        
        # Convert to pandas DataFrame for better formatting
        df = results.to_dataframe()
        
        if len(df) == 0:
            return "Query executed successfully but returned 0 rows."
        
        # Format results nicely
        result_str = f"Query returned {len(df)} rows:\n\n"
        result_str += df.to_string(index=False)
        
        return result_str
        
    except Exception as e:
        return f"❌ Query Error: {str(e)}"


# ============================================
# TOOL 2: Get Table Schema
# ============================================

@tool
def get_table_schema(table_name: str) -> str:
    """
    Get the schema (column names and types) of a BigQuery table.
    
    Use this when you need to understand table structure before writing queries.
    
    Args:
        table_name: Name of the table (e.g., 'prescription_claims', 'member_demographics')
        
    Returns:
        Table schema with column names, types, and descriptions
    """
    
    try:
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = bq_client.get_table(full_table_id)
        
        schema_str = f"Schema for {table_name}:\n"
        schema_str += f"Total rows: {table.num_rows:,}\n\n"
        schema_str += "Columns:\n"
        
        for field in table.schema:
            schema_str += f"  - {field.name} ({field.field_type})"
            if field.description:
                schema_str += f": {field.description}"
            schema_str += "\n"
        
        return schema_str
        
    except Exception as e:
        return f"❌ Error getting schema: {str(e)}"


# ============================================
# TOOL 3: Calculate Metric
# ============================================

@tool
def calculate_pharmacy_metric(metric_name: str, time_period: Optional[str] = "last_90_days") -> str:
    """
    Calculate common pharmacy KPIs automatically.
    
    Available metrics:
    - generic_dispensing_rate (GDR)
    - pmpm (Per Member Per Month cost)
    - specialty_proportion (% of costs from specialty drugs)
    - total_cost
    - claim_volume
    
    Args:
        metric_name: Name of the metric to calculate
        time_period: Time period (last_30_days, last_90_days, last_year, all_time)
        
    Returns:
        Calculated metric value with context
    """
    
    try:
        # Map time periods to SQL
        time_filters = {
            "last_30_days": "fill_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)",
            "last_90_days": "fill_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)",
            "last_year": "fill_date >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 YEAR)",
            "all_time": "1=1"  # No filter
        }
        
        time_filter = time_filters.get(time_period, time_filters["last_90_days"])
        
        # Define metric queries
        if metric_name.lower() == "generic_dispensing_rate" or metric_name.lower() == "gdr":
            sql = f"""
            SELECT 
                ROUND(SUM(CASE WHEN is_generic THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as gdr
            FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`
            WHERE {time_filter}
            """
            
        elif metric_name.lower() == "pmpm":
            sql = f"""
            WITH cost_data AS (
                SELECT 
                    SUM(drug_cost) as total_cost,
                    COUNT(DISTINCT member_id) as member_count,
                    DATE_DIFF(MAX(fill_date), MIN(fill_date), DAY) / 30.0 as months
                FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`
                WHERE {time_filter}
            )
            SELECT 
                ROUND(total_cost / (member_count * months), 2) as pmpm
            FROM cost_data
            """
            
        elif metric_name.lower() == "specialty_proportion":
            sql = f"""
            WITH costs AS (
                SELECT 
                    SUM(CASE WHEN drug_category = 'Specialty' THEN drug_cost ELSE 0 END) as specialty_cost,
                    SUM(drug_cost) as total_cost
                FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`
                WHERE {time_filter}
            )
            SELECT 
                ROUND(specialty_cost * 100.0 / total_cost, 2) as specialty_pct
            FROM costs
            """
            
        elif metric_name.lower() == "total_cost":
            sql = f"""
            SELECT 
                ROUND(SUM(drug_cost), 2) as total_cost,
                COUNT(*) as claim_count
            FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`
            WHERE {time_filter}
            """
            
        elif metric_name.lower() == "claim_volume":
            sql = f"""
            SELECT 
                COUNT(*) as total_claims,
                COUNT(DISTINCT member_id) as unique_members
            FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`
            WHERE {time_filter}
            """
        else:
            return f"❌ Unknown metric: {metric_name}. Available metrics: generic_dispensing_rate, pmpm, specialty_proportion, total_cost, claim_volume"
        
        # Execute query
        query_job = bq_client.query(sql)
        results = query_job.result()
        df = results.to_dataframe()
        
        # Format result
        result_str = f"📊 {metric_name.upper()} ({time_period}):\n\n"
        result_str += df.to_string(index=False)
        
        return result_str
        
    except Exception as e:
        return f"❌ Error calculating metric: {str(e)}"


# ============================================
# TOOL 4: Search Documentation (from RAG)
# ============================================

# This will be imported and used by the agent
# We'll integrate it in the next step

# Test the tools
if __name__ == "__main__":
    print("="*60)
    print("Testing PharmEngine AI Tools")
    print("="*60 + "\n")
    
    # Test 1: Simple query
    print("Test 1: Count total claims")
    print("-"*60)
    result = execute_sql_query.invoke({
        "sql": f"SELECT COUNT(*) as total_claims FROM `{PROJECT_ID}.{DATASET_ID}.prescription_claims`"
    })
    print(result)
    
    # Test 2: Get schema
    print("\n\nTest 2: Get table schema")
    print("-"*60)
    result = get_table_schema.invoke({"table_name": "prescription_claims"})
    print(result[:500] + "..." if len(result) > 500 else result)
    
    # Test 3: Calculate metric
    print("\n\nTest 3: Calculate GDR")
    print("-"*60)
    result = calculate_pharmacy_metric.invoke({
        "metric_name": "generic_dispensing_rate",
        "time_period": "last_90_days"
    })
    print(result)
    
    print("\n" + "="*60)
    print("✅ Tools Test Complete")
    print("="*60)