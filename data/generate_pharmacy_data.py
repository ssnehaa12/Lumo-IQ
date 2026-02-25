"""
Generate synthetic pharmacy claims data for PharmEngine AI
Creates realistic healthcare data and loads to BigQuery
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.cloud import bigquery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GCP_PROJECT_ID')
DATASET_ID = os.getenv('BIGQUERY_DATASET')
LOCATION = 'US'

print(f"🏥 PharmEngine AI - Data Generator")
print(f"📊 Project: {PROJECT_ID}")
print(f"📁 Dataset: {DATASET_ID}")
print("="*60)

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# ============================================
# CONFIGURATION: Drug Information
# ============================================
DRUG_CATALOG = {
    'ATORVASTATIN': {
        'category': 'Cardiovascular',
        'avg_cost': 25,
        'generic': True,
        'tier': 1,
        'frequency': 0.15  # 15% of prescriptions
    },
    'LISINOPRIL': {
        'category': 'Cardiovascular',
        'avg_cost': 18,
        'generic': True,
        'tier': 1,
        'frequency': 0.15
    },
    'METFORMIN': {
        'category': 'Diabetes',
        'avg_cost': 12,
        'generic': True,
        'tier': 1,
        'frequency': 0.12
    },
    'INSULIN GLARGINE': {
        'category': 'Diabetes',
        'avg_cost': 350,
        'generic': False,
        'tier': 3,
        'frequency': 0.05
    },
    'OMEPRAZOLE': {
        'category': 'GI',
        'avg_cost': 20,
        'generic': True,
        'tier': 1,
        'frequency': 0.10
    },
    'PANTOPRAZOLE': {
        'category': 'GI',
        'avg_cost': 450,
        'generic': False,
        'tier': 2,
        'frequency': 0.03
    },
    'SERTRALINE': {
        'category': 'Mental Health',
        'avg_cost': 15,
        'generic': True,
        'tier': 1,
        'frequency': 0.12
    },
    'ESCITALOPRAM': {
        'category': 'Mental Health',
        'avg_cost': 22,
        'generic': True,
        'tier': 1,
        'frequency': 0.08
    },
    'ADALIMUMAB': {
        'category': 'Specialty',
        'avg_cost': 5500,
        'generic': False,
        'tier': 4,
        'frequency': 0.05
    },
    'TRASTUZUMAB': {
        'category': 'Specialty',
        'avg_cost': 6200,
        'generic': False,
        'tier': 4,
        'frequency': 0.05
    },
    'LEVOTHYROXINE': {
        'category': 'Endocrine',
        'avg_cost': 14,
        'generic': True,
        'tier': 1,
        'frequency': 0.10
    }
}

# ============================================
# FUNCTION: Generate Prescription Claims
# ============================================
def generate_prescription_claims(n_rows=50000):
    """Generate realistic pharmacy claims data"""
    
    print(f"\n📋 Generating {n_rows:,} prescription claims...")
    
    np.random.seed(42)  # For reproducibility
    
    drugs = list(DRUG_CATALOG.keys())
    frequencies = [DRUG_CATALOG[d]['frequency'] for d in drugs]
    
    # Normalize frequencies to sum to 1
    frequencies = np.array(frequencies) / sum(frequencies)
    
    # Generate dates (last 2 years, with trend toward recent)
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    date_range_days = (end_date - start_date).days
    
    # More recent claims are more common (realistic pattern)
    dates = []
    for _ in range(n_rows):
        # Weighted toward recent dates
        days_ago = int(np.random.exponential(date_range_days / 3))
        days_ago = min(days_ago, date_range_days)
        fill_date = end_date - timedelta(days=days_ago)
        dates.append(fill_date)
    
    # Generate claims
    data = {
        'claim_id': [f"CLM{i:08d}" for i in range(1, n_rows + 1)],
        'fill_date': dates,
        'member_id': [f"MBR{np.random.randint(1, 10001):06d}" for _ in range(n_rows)],
        'drug_name': np.random.choice(drugs, n_rows, p=frequencies),
        'quantity': np.random.choice([30, 60, 90], n_rows, p=[0.60, 0.25, 0.15]),
        'days_supply': np.random.choice([30, 60, 90], n_rows, p=[0.60, 0.25, 0.15]),
    }
    
    df = pd.DataFrame(data)
    
    # Add drug details
    df['drug_category'] = df['drug_name'].map(lambda x: DRUG_CATALOG[x]['category'])
    df['is_generic'] = df['drug_name'].map(lambda x: DRUG_CATALOG[x]['generic'])
    df['tier'] = df['drug_name'].map(lambda x: DRUG_CATALOG[x]['tier'])
    df['base_cost'] = df['drug_name'].map(lambda x: DRUG_CATALOG[x]['avg_cost'])
    
    # Add realistic cost variation (±10%)
    df['drug_cost'] = df['base_cost'] * np.random.uniform(0.90, 1.10, n_rows)
    
    # Calculate copays based on tier
    def calculate_copay(row):
        if row['tier'] == 1:  # Generic
            return np.random.choice([5, 10, 15])
        elif row['tier'] == 2:  # Preferred brand
            return np.random.choice([30, 40, 50])
        elif row['tier'] == 3:  # Non-preferred brand
            return np.random.choice([50, 65, 75])
        else:  # Specialty (tier 4)
            return min(np.random.choice([75, 100, 150, 200]), row['drug_cost'] * 0.3)
    
    df['copay'] = df.apply(calculate_copay, axis=1)
    
    # Add pharmacy details
    df['pharmacy_id'] = [f"PHM{np.random.randint(1, 501):04d}" for _ in range(n_rows)]
    df['pharmacy_type'] = np.random.choice(
        ['Retail', 'Mail Order', 'Specialty'], 
        n_rows, 
        p=[0.70, 0.22, 0.08]
    )
    
    # Specialty drugs should mostly come from specialty pharmacies
    specialty_mask = df['drug_category'] == 'Specialty'
    df.loc[specialty_mask, 'pharmacy_type'] = np.random.choice(
        ['Specialty', 'Retail'], 
        specialty_mask.sum(), 
        p=[0.85, 0.15]
    )
    
    # Drop temporary column
    df = df.drop('base_cost', axis=1)
    
    print(f"✓ Generated {len(df):,} claims")
    print(f"  - Date range: {df['fill_date'].min().date()} to {df['fill_date'].max().date()}")
    print(f"  - Unique members: {df['member_id'].nunique():,}")
    print(f"  - Total drug cost: ${df['drug_cost'].sum():,.2f}")
    print(f"  - Generic rate: {(df['is_generic'].sum() / len(df) * 100):.1f}%")
    
    return df

# ============================================
# FUNCTION: Generate Member Demographics
# ============================================
def generate_member_demographics(n_members=10000):
    """Generate member demographic data"""
    
    print(f"\n👥 Generating {n_members:,} member demographics...")
    
    np.random.seed(42)
    
    data = {
        'member_id': [f"MBR{i:06d}" for i in range(1, n_members + 1)],
        'age': np.random.choice(range(18, 90), n_members),
        'gender': np.random.choice(['M', 'F'], n_members),
        'state': np.random.choice(
        ['CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI'], 
        n_members, 
        ),
        'plan_type': np.random.choice(
            ['Commercial', 'Medicare', 'Medicaid'], 
            n_members, 
            p=[0.50, 0.30, 0.20]
        ),
        'chronic_conditions': np.random.choice(
            [0, 1, 2, 3, 4], 
            n_members, 
            p=[0.30, 0.30, 0.20, 0.15, 0.05]
        )
    }
    
    df = pd.DataFrame(data)
    
    # Calculate risk score (higher for older age, more conditions)
    df['risk_score'] = (
        (df['age'] / 100) + 
        (df['chronic_conditions'] * 0.3)
    ) * np.random.uniform(0.8, 1.2, n_members)
    
    # Round risk score
    df['risk_score'] = df['risk_score'].round(2)
    
    print(f"✓ Generated {len(df):,} members")
    print(f"  - Age range: {df['age'].min()} to {df['age'].max()}")
    print(f"  - Avg risk score: {df['risk_score'].mean():.2f}")
    print(f"  - High-risk (score > 2.0): {(df['risk_score'] > 2.0).sum():,} members")
    
    return df

# ============================================
# FUNCTION: Generate Drug Formulary
# ============================================
def generate_formulary():
    """Generate formulary tier information"""
    
    print(f"\n💊 Generating drug formulary...")
    
    formulary_data = []
    
    for drug_name, info in DRUG_CATALOG.items():
        formulary_data.append({
            'drug_name': drug_name,
            'drug_category': info['category'],
            'tier': info['tier'],
            'is_generic': info['generic'],
            'prior_auth_required': info['tier'] >= 3,
            'step_therapy_required': info['tier'] >= 3,
            'preferred_alternative': None if info['generic'] else 'GENERIC_EQUIVALENT',
            'awp_cost': info['avg_cost']
        })
    
    df = pd.DataFrame(formulary_data)
    
    print(f"✓ Generated formulary for {len(df)} drugs")
    
    return df

# ============================================
# FUNCTION: Upload to BigQuery
# ============================================
def upload_to_bigquery(df, table_name, schema=None):
    """Upload dataframe to BigQuery"""
    
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    
    print(f"\n☁️  Uploading to BigQuery: {table_id}")
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite if exists
        schema=schema
    )
    
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Wait for job to complete
    
    table = client.get_table(table_id)
    print(f"✓ Loaded {table.num_rows:,} rows into {table_id}")
    
    return table_id

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    try:
        print("\n🚀 Starting data generation...\n")
        
        # Generate data
        claims_df = generate_prescription_claims(50000)
        members_df = generate_member_demographics(10000)
        formulary_df = generate_formulary()
        
        # Upload to BigQuery
        print("\n" + "="*60)
        print("📤 UPLOADING TO BIGQUERY")
        print("="*60)
        
        # Table 1: Prescription Claims
        claims_schema = [
            bigquery.SchemaField("claim_id", "STRING"),
            bigquery.SchemaField("fill_date", "TIMESTAMP"),
            bigquery.SchemaField("member_id", "STRING"),
            bigquery.SchemaField("drug_name", "STRING"),
            bigquery.SchemaField("drug_category", "STRING"),
            bigquery.SchemaField("is_generic", "BOOLEAN"),
            bigquery.SchemaField("tier", "INTEGER"),
            bigquery.SchemaField("quantity", "INTEGER"),
            bigquery.SchemaField("days_supply", "INTEGER"),
            bigquery.SchemaField("drug_cost", "FLOAT"),
            bigquery.SchemaField("copay", "FLOAT"),
            bigquery.SchemaField("pharmacy_id", "STRING"),
            bigquery.SchemaField("pharmacy_type", "STRING"),
        ]
        upload_to_bigquery(claims_df, "prescription_claims", claims_schema)
        
        # Table 2: Member Demographics
        upload_to_bigquery(members_df, "member_demographics")
        
        # Table 3: Drug Formulary
        upload_to_bigquery(formulary_df, "drug_formulary")
        
        print("\n" + "="*60)
        print("✅ DATA GENERATION COMPLETE!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • {len(claims_df):,} prescription claims")
        print(f"  • {len(members_df):,} member records")
        print(f"  • {len(formulary_df)} formulary entries")
        print(f"\n🔗 View in BigQuery Console:")
        print(f"  https://console.cloud.google.com/bigquery?project={PROJECT_ID}&d={DATASET_ID}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise