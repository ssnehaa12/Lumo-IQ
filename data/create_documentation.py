"""
Create business documentation for PharmEngine AI RAG system
Uploads to Google Cloud Storage
"""

from google.cloud import storage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv('GCP_PROJECT_ID')
BUCKET_NAME = os.getenv('GCS_DOCS_BUCKET')

print(f"📚 PharmEngine AI - Documentation Generator")
print(f"🪣 Bucket: {BUCKET_NAME}")
print("="*60)

# Initialize GCS client
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

# ============================================
# DOCUMENT 1: DATA DICTIONARY
# ============================================
data_dictionary = """# PharmEngine Analytics - Data Dictionary

## Overview
This data dictionary describes the pharmacy claims analytics data warehouse for PharmEngine AI.
All data is synthetic but follows real-world pharmacy claims patterns and structures.

---

## Table: prescription_claims

### Business Description
Contains all pharmacy claims submitted for prescription medications. Each row represents 
a single prescription fill event. This is the primary transactional table used for 
utilization analysis, trend monitoring, cost management, and adherence tracking.

### Technical Details
- **Row Count:** ~50,000 claims
- **Time Period:** 2023-01-01 to present
- **Grain:** One row per prescription fill
- **Primary Key:** claim_id
- **Foreign Keys:** member_id (links to member_demographics)

### Columns

**claim_id** (STRING)
- Unique identifier for each pharmacy claim
- Format: CLM + 8-digit number (e.g., CLM00012345)
- Used for claim-level tracking and reconciliation

**fill_date** (TIMESTAMP)
- Date and time the prescription was filled at pharmacy
- Used for trend analysis, seasonality detection, time series forecasting
- Timezone: UTC

**member_id** (STRING)
- Unique member/patient identifier
- Format: MBR + 6-digit number (e.g., MBR001234)
- Links to member_demographics table for patient-level analysis
- De-identified for privacy compliance

**drug_name** (STRING)
- Generic or brand name of dispensed medication
- Standardized naming convention (all uppercase)
- Examples: ATORVASTATIN, METFORMIN, ADALIMUMAB
- Links to drug_formulary table for tier/coverage information

**drug_category** (STRING)
- Therapeutic class/category of medication
- Values: 
  - Cardiovascular (blood pressure, cholesterol, heart)
  - Diabetes (insulin, oral diabetes medications)
  - GI (gastrointestinal/stomach medications)
  - Mental Health (antidepressants, anxiety)
  - Specialty (high-cost biologics for complex conditions)
  - Endocrine (thyroid, hormones)

**is_generic** (BOOLEAN)
- TRUE if generic drug dispensed
- FALSE if brand name drug dispensed
- Key metric: Generic Dispensing Rate (GDR) target is >85%
- Generic drugs typically cost 80-85% less than brand equivalents

**tier** (INTEGER)
- Formulary tier placement (1-4)
- Tier 1: Preferred generic (lowest cost sharing)
- Tier 2: Generic or preferred brand
- Tier 3: Non-preferred brand (higher cost sharing)
- Tier 4: Specialty drugs (highest cost sharing)
- Lower tiers = lower member copays = better adherence

**quantity** (INTEGER)
- Number of units dispensed (tablets, capsules, milliliters, etc.)
- Common values: 30, 60, 90 (corresponding to days supply)
- Used for quantity limit enforcement and utilization management

**days_supply** (INTEGER)
- Duration of medication supply in days
- Standard values: 30, 60, 90
- Should generally match quantity for solid oral dosage forms
- Used for adherence calculations (PDC - Proportion of Days Covered)
- 90-day supplies (mail order) often have better adherence rates

**drug_cost** (FLOAT)
- Total drug cost in USD
- Includes ingredient cost + dispensing fee
- Represents total plan + member cost
- Does NOT include rebates (those are calculated separately)
- Average ranges: $10-30 (generic), $300-500 (brand), $5000-7000 (specialty)

**copay** (FLOAT)
- Member out-of-pocket cost in USD at point of sale
- Varies by formulary tier:
  - Tier 1: $5-15
  - Tier 2: $30-50  
  - Tier 3: $50-75
  - Tier 4: $75-200+ (or percentage coinsurance)
- Lower copays improve medication adherence

**pharmacy_id** (STRING)
- Unique pharmacy location identifier
- Format: PHM + 4-digit number (e.g., PHM0123)
- Used for pharmacy network analysis and performance monitoring

**pharmacy_type** (STRING)
- Channel of dispensing
- Values:
  - Retail: Traditional brick-and-mortar pharmacies (70% of claims)
  - Mail Order: Home delivery pharmacy (22% of claims)
  - Specialty: Specialty pharmacies for complex medications (8% of claims)
- Specialty drugs should primarily use specialty pharmacies

---

## Table: member_demographics

### Business Description
Member-level demographic and risk information. One row per unique member.
Used for population health analysis, risk stratification, and targeted interventions.

### Technical Details
- **Row Count:** ~10,000 members
- **Grain:** One row per member
- **Primary Key:** member_id

### Columns

**member_id** (STRING)
- Unique member identifier
- Primary key, links to prescription_claims table

**age** (INTEGER)
- Member age in years
- Range: 18-89
- Used for age-based analysis and CMS Star Ratings stratification

**gender** (STRING)
- Member gender
- Values: M (Male), F (Female)

**state** (STRING)
- Two-letter state code of member residence
- Used for geographic analysis and state-specific programs

**plan_type** (STRING)
- Insurance plan category
- Values:
  - Commercial: Employer-sponsored insurance (50% of members)
  - Medicare: Federal insurance for 65+ or disabled (30%)
  - Medicaid: State/federal insurance for low-income (20%)
- Different plan types have different cost structures and regulations

**chronic_conditions** (INTEGER)
- Count of chronic disease conditions
- Range: 0-4
- Common conditions: diabetes, hypertension, COPD, CHF, asthma
- Members with 3+ conditions are "high-risk" and need care management

**risk_score** (FLOAT)
- Predicted healthcare cost risk score
- Range: ~0.5 to 3.5
- Higher score = higher expected costs
- Based on age, chronic conditions, and historical utilization
- Used for care management program targeting and budget forecasting
- Scores >2.0 typically qualify for high-risk programs

---

## Table: drug_formulary

### Business Description
Formulary tier placement and management criteria for medications.
Defines coverage rules, cost sharing, and clinical management requirements.

### Technical Details
- **Row Count:** 11 drugs
- **Grain:** One row per drug
- **Primary Key:** drug_name

### Columns

**drug_name** (STRING)
- Medication name (primary key)

**drug_category** (STRING)
- Therapeutic category

**tier** (INTEGER)
- Formulary tier (1-4)
- Determines member cost sharing

**is_generic** (BOOLEAN)
- Generic vs brand status

**prior_auth_required** (BOOLEAN)
- TRUE if prior authorization needed before filling prescription
- Physician must justify medical necessity
- Typically required for tier 3-4 drugs
- Ensures appropriate utilization and cost management

**step_therapy_required** (BOOLEAN)
- TRUE if member must try lower-cost alternatives first
- Also called "fail first" policy
- Example: Must try generic omeprazole before brand Pantoprazole
- Reduces unnecessary use of expensive medications

**preferred_alternative** (STRING)
- Recommended lower-cost alternative drug
- NULL if no alternative exists
- Used in therapeutic substitution programs

**awp_cost** (FLOAT)
- Average Wholesale Price in USD
- Benchmark pricing used for reimbursement calculations
- Does NOT include dispensing fees or rebates

---

## Common Queries & Use Cases

### Utilization Analysis
```sql
-- Monthly claim trends
SELECT 
  DATE_TRUNC(fill_date, MONTH) as month,
  COUNT(*) as claims,
  SUM(drug_cost) as total_cost
FROM prescription_claims
GROUP BY 1
ORDER BY 1 DESC

-- Top drugs by cost
SELECT 
  drug_name,
  COUNT(*) as fills,
  SUM(drug_cost) as total_cost
FROM prescription_claims
WHERE fill_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY 1
ORDER BY 3 DESC
LIMIT 10
```

### Generic Dispensing Rate (GDR)
```sql
SELECT 
  SUM(CASE WHEN is_generic THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as gdr
FROM prescription_claims
WHERE fill_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
```

### High-Risk Member Identification
```sql
SELECT 
  m.member_id,
  m.age,
  m.chronic_conditions,
  m.risk_score,
  COUNT(c.claim_id) as claim_count,
  SUM(c.drug_cost) as total_drug_cost
FROM member_demographics m
LEFT JOIN prescription_claims c ON m.member_id = c.member_id
WHERE m.risk_score > 2.0
GROUP BY 1,2,3,4
ORDER BY 6 DESC
```

### Specialty Drug Analysis
```sql
SELECT 
  drug_name,
  COUNT(*) as claim_count,
  SUM(drug_cost) as total_cost,
  AVG(drug_cost) as avg_cost_per_claim
FROM prescription_claims
WHERE drug_category = 'Specialty'
  AND fill_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
GROUP BY 1
ORDER BY 3 DESC
```

---

## Data Quality Notes

- **Completeness:** All required fields are populated (no nulls in key columns)
- **Referential Integrity:** All member_ids in claims exist in demographics table
- **Date Range:** Claims span from 2023-01-01 to current date
- **Realistic Patterns:** Data includes seasonal variation and trend patterns
- **Synthetic Data:** All data is synthetic; no real patient information
"""

# ============================================
# DOCUMENT 2: BUSINESS GLOSSARY
# ============================================
business_glossary = """# PharmEngine - Business Glossary & KPI Reference

## Key Performance Indicators (KPIs)

### Generic Dispensing Rate (GDR)
**Definition:** Percentage of prescriptions filled with generic drugs

**Formula:** (Generic Drug Fills / Total Fills) × 100

**Target:** >85% (industry benchmark)

**Why It Matters:** 
- Generic drugs cost 80-85% less than brand equivalents
- Higher GDR = significant cost savings with no quality compromise
- FDA requires generics to be bioequivalent to brands
- Every 1% increase in GDR saves ~$300K annually (for typical plan)

**Current Performance:** 81.7% (below target - opportunity for improvement)

**Improvement Strategies:**
- Formulary incentives (lower generic copays)
- Prescriber education on generic equivalence
- Prior authorization on brands with generic alternatives
- Generic substitution programs at pharmacy

---

### Per Member Per Month Cost (PMPM)
**Definition:** Average pharmacy spend per member per month

**Formula:** Total Drug Cost / (Member Count × Number of Months)

**Benchmark Range:** 
- Commercial: $50-100 PMPM
- Medicare: $150-250 PMPM  
- Specialty-heavy populations: $200-400 PMPM

**Why It Matters:**
- Standard industry metric for cost management
- Used for budgeting and trend forecasting
- Enables benchmarking against other plans
- Helps identify cost drivers and outliers

**Components:**
- Retail pharmacy costs (~40%)
- Mail order costs (~15%)
- Specialty pharmacy costs (~45%)

---

### Specialty Drug Proportion
**Definition:** Percentage of total pharmacy costs from specialty drugs

**Formula:** (Specialty Drug Cost / Total Drug Cost) × 100

**Typical Range:** 40-50% of costs, but only 1-2% of prescription volume

**Why It Matters:**
- Specialty drugs are the #1 cost driver in pharmacy
- Growing at 10-15% annually (vs 2-3% for traditional drugs)
- Often treat chronic, complex conditions (cancer, autoimmune, MS)
- Require specialized handling, storage, and patient support

**Management Strategies:**
- Prior authorization to ensure appropriate use
- Specialty pharmacy network with better pricing
- Patient assistance programs and manufacturer copay support
- Biosimilar adoption where clinically appropriate

---

### Medication Adherence Rate (PDC)
**Definition:** Proportion of Days Covered - measures if patient takes medication as prescribed

**Formula:** (Days with Medication On Hand / Days in Measurement Period) × 100

**Target:** >80% (CMS Star Ratings threshold)

**Why It Matters:**
- Better adherence = better health outcomes
- Poor adherence leads to:
  - More ER visits and hospitalizations
  - Disease progression
  - Higher total medical costs
- CMS Star Ratings impact Medicare plan payments
- Key quality measure for diabetes, hypertension, cholesterol meds

**Factors Affecting Adherence:**
- High copays (biggest barrier)
- Complex regimens (multiple daily doses)
- Side effects
- Lack of patient education
- Access/convenience issues

**Improvement Strategies:**
- Reduce copays for chronic disease medications
- 90-day mail order (convenience + lower costs)
- Patient reminders and educational outreach
- Pharmacist counseling programs
- Synchronize medication refills

---

## Therapeutic Categories

### Cardiovascular
**Common Conditions:** High blood pressure, high cholesterol, heart failure

**Key Drugs:** 
- ATORVASTATIN (Lipitor) - cholesterol
- LISINOPRIL - blood pressure
- METOPROLOL - heart rate/blood pressure

**Cost Profile:** Generally low-cost; most are generic

**Clinical Notes:** 
- High-adherence therapeutic class (patients feel benefit)
- Evidence-based for preventing heart attacks and strokes

---

### Diabetes
**Common Conditions:** Type 1 and Type 2 diabetes

**Key Drugs:**
- METFORMIN - first-line oral medication (generic, cheap)
- INSULIN GLARGINE (Lantus) - long-acting insulin (expensive)
- GLP-1 agonists - newer class (very expensive)

**Cost Profile:** Wide range - $10/month for metformin to $500+/month for newer insulins

**Clinical Notes:**
- Adherence is critical to prevent complications
- Insulin is life-saving for Type 1 diabetes
- Cost barriers are significant problem

---

### Mental Health
**Common Conditions:** Depression, anxiety, ADHD

**Key Drugs:**
- SERTRALINE (Zoloft) - antidepressant
- ESCITALOPRAM (Lexapro) - antidepressant
- BUPROPION - depression/smoking cessation

**Cost Profile:** Mostly generic, low-cost

**Clinical Notes:**
- Adherence challenges due to stigma and side effects
- Often require 4-6 weeks to see effect
- Sudden discontinuation can cause withdrawal

---

### Specialty
**Common Conditions:** Cancer, rheumatoid arthritis, multiple sclerosis, Crohn's disease

**Key Drugs:**
- ADALIMUMAB (Humira) - autoimmune conditions ($5500/fill)
- TRASTUZUMAB (Herceptin) - breast cancer ($6200/fill)

**Cost Profile:** $5,000-15,000+ per month

**Clinical Notes:**
- Often injectables or infusions
- Require special handling (refrigeration)
- Patient support services critical
- Biosimilars now available (20-30% cost savings)

---

## Formulary Management Terms

### Prior Authorization (PA)
**Definition:** Requirement for physician to obtain approval before drug is covered

**Purpose:**
- Ensure medical appropriateness
- Encourage use of preferred alternatives
- Manage high-cost medications
- Prevent off-label use without evidence

**Typical Criteria:**
- Diagnosis code matches FDA indication
- Patient tried and failed lower-cost alternatives
- Dosing is within guidelines
- No contraindications

**Impact:** 
- 10-15% claim denial rate
- Delays treatment by 1-3 days on average
- Administrative burden on physicians
- But saves significant costs by reducing inappropriate use

---

### Step Therapy
**Definition:** Requirement to try lower-cost medication before approving expensive alternative

**Also Called:** "Fail first" policy

**Example:** 
- Step 1: Try generic omeprazole ($20/month)
- Step 2: If ineffective, approve brand Pantoprazole ($450/month)

**Rationale:** Many patients respond to cheaper option; only use expensive drug if truly needed

**Controversy:** 
- Physicians argue it delays optimal treatment
- Plans argue it prevents unnecessary costs
- Evidence shows 60-70% of patients succeed on Step 1

---

### Formulary Tiers
**Purpose:** Tiered copay structure to incentivize lower-cost medications

**Typical Structure:**

**Tier 1 - Preferred Generic**
- Copay: $5-15
- Lowest cost sharing
- Includes most common generic medications
- Goal: Make generics most affordable option

**Tier 2 - Generic / Preferred Brand**
- Copay: $30-50
- Non-preferred generics or preferred brands with no generic
- Moderate cost sharing

**Tier 3 - Non-Preferred Brand**
- Copay: $50-75
- Brand drugs with generic alternatives available
- Higher cost sharing to discourage use

**Tier 4 - Specialty**
- Copay: $75-200+ or 20-33% coinsurance
- High-cost specialty medications
- Often has out-of-pocket maximum protection

---

## Cost Management Strategies

### 1. Generic Conversion
**Strategy:** Switch brand drugs to generic when available

**Savings Potential:** $200-500 per prescription annually

**Implementation:**
- Automated substitution at pharmacy (when allowed by state law)
- Prescriber education campaigns
- Lower copays for generics (tier 1 vs tier 3)
- Prior authorization on brands with generic alternatives

---

### 2. Therapeutic Substitution
**Strategy:** Switch to clinically equivalent, lower-cost alternative in same class

**Example:** Switch Nexium (brand PPI) to omeprazole (generic PPI)

**Requirements:**
- Physician approval (cannot be done automatically)
- Evidence of clinical equivalence
- Patient education

**Savings:** 40-60% cost reduction

---

### 3. Quantity Limits
**Strategy:** Restrict quantities to appropriate, evidence-based amounts

**Purpose:**
- Prevent stockpiling
- Reduce waste
- Ensure appropriate dosing
- Control costs

**Example:** Limit erectile dysfunction medications to 8 tablets per month

---

### 4. Mail Order Incentives
**Strategy:** Encourage 90-day mail order fills with lower copays

**Benefits:**
- Lower copay ($90 for 90-day supply vs $45 × 3 = $135 for three 30-day retail fills)
- Better adherence (fewer refill trips)
- Lower dispensing fees (1 fill vs 3)
- Convenience for patients with chronic conditions

**Typical Adoption:** 20-25% of maintenance medications

---

### 5. Specialty Pharmacy Network
**Strategy:** Channel high-cost specialty drugs through preferred specialty pharmacies

**Benefits:**
- Better pricing through volume contracts
- Clinical oversight and patient support services
- Ensure appropriate handling and administration
- Prior authorization compliance

**Savings:** 15-25% on specialty drug costs

---

## Quality Metrics & Star Ratings

### CMS Star Ratings
**Definition:** CMS quality rating system for Medicare plans (1-5 stars)

**Impact:**
- Plans with 4+ stars get bonus payments
- Higher stars = better member enrollment
- Pharmacy measures account for ~40% of overall rating

**Key Pharmacy Measures:**
- Adherence to diabetes medications (PDC >80%)
- Adherence to hypertension medications (PDC >80%)
- Adherence to cholesterol medications (PDC >80%)
- Medication Therapy Management (MTM) program completion

---

### HEDIS Measures
**Definition:** Healthcare Effectiveness Data and Information Set

**Common Pharmacy-Related Measures:**
- Antidepressant medication management
- Persistence of beta-blocker treatment after heart attack
- Diabetes medication adherence
- Asthma controller medication use

**Purpose:** Standardized quality measurement for health plans

---

## Business Intelligence Terms

### Trend Analysis
Looking at metrics over time to identify patterns, seasonality, and trajectory

**Example:** "Specialty drug costs increased 18% from Q4 2023 to Q4 2024"

---

### Root Cause Analysis
Investigating WHY a metric changed

**Example:** "Specialty costs increased because 45 additional members started Adalimumab therapy"

---

### Predictive Analytics
Using historical data to forecast future trends

**Example:** "Based on current trajectory, we project $38M in specialty costs next year"

---

### Segmentation
Dividing population into groups for targeted analysis or interventions

**Example:** "High-risk members (risk score >2.0) account for 35% of total pharmacy costs"

---

## Common Business Questions

### Cost Driver Analysis
"What's driving our pharmacy cost increases?"
- Look at drug category trends
- Identify high-cost drugs with volume increases
- Check for new market entrants (new expensive drugs launched)
- Analyze member mix changes (more high-risk members?)

### Formulary Optimization
"What formulary changes would save the most money?"
- Identify brand drugs with generic alternatives where utilization is high
- Calculate savings from tier changes
- Model impact of prior authorization policies
- Assess biosimilar adoption opportunities

### Member Risk Stratification
"Which members need proactive intervention?"
- High-risk scores (>2.0)
- Multiple chronic conditions (3+)
- High specialty drug costs
- Poor medication adherence
- Frequent ER visits (from medical claims)

### Network Performance
"How do our pharmacies perform?"
- Compare costs across pharmacy types
- Analyze adherence by pharmacy
- Identify outliers (unusually high costs or low quality)
- Evaluate specialty pharmacy performance

---

## Data-Driven Decision Making

The goal of PharmEngine AI is to make these complex analyses accessible through natural language.

Instead of writing SQL queries, business users can ask:
- "Why did specialty costs spike in Q4?"
- "Which members would benefit from adherence outreach?"
- "What's the ROI of adding prior auth to Drug X?"

The AI agent will:
1. Understand the business question
2. Query the appropriate data
3. Perform relevant analysis
4. Generate actionable insights
5. Provide recommendations with expected impact
"""

# ============================================
# DOCUMENT 3: EXAMPLE ANALYSIS
# ============================================
example_analysis = """# Example Analysis: Q4 2024 Specialty Drug Cost Investigation

## Executive Summary

Specialty drug costs increased **$1.8M (+18%)** in Q4 2024 vs Q4 2023, primarily driven by 
increased utilization of ADALIMUMAB (Humira biosimilar) for autoimmune conditions.

**Key Findings:**
- New member starts increased 45% (35 new members on ADALIMUMAB)
- Average cost per claim remained stable (~$5,500)
- Opportunity: Implement prior authorization → Est. $2.1M annual savings

---

## Detailed Analysis

### 1. Cost Trend

**Q4 2023:**
- Total specialty cost: $9.8M
- Claim volume: 1,245 claims
- Average cost per claim: $7,871

**Q4 2024:**
- Total specialty cost: $11.6M  
- Claim volume: 1,567 claims (+26%)
- Average cost per claim: $7,402 (-6%)

**Insight:** Volume increased 26% but unit cost decreased 6%, indicating good pricing but 
utilization growth is the driver.

---

### 2. Drug-Level Detail

| Drug | Q4 2023 Claims | Q4 2024 Claims | Change | Q4 2024 Cost |
|------|----------------|----------------|--------|--------------|
| ADALIMUMAB | 567 | 823 | +45% | $4.5M |
| TRASTUZUMAB | 678 | 744 | +10% | $4.6M |
| **Total Specialty** | **1,245** | **1,567** | **+26%** | **$11.6M** |

**Insight:** ADALIMUMAB is the primary driver, growing 45% year-over-year.

---

### 3. Member Analysis

**New Starts (Q4 2024):**
- 35 members started ADALIMUMAB therapy in Q4 2024
- Average age: 52 years
- 80% have rheumatoid arthritis or Crohn's disease diagnosis
- 65% are Medicare members

**Member Risk Profile:**
- Average risk score: 2.8 (high risk)
- Average chronic conditions: 3.2
- These are clinically appropriate, high-need patients

---

### 4. Clinical Appropriateness Review

**Good News:** 
- All 35 new starts had appropriate diagnosis codes
- 94% had documentation of failed conventional therapy
- No obvious signs of inappropriate utilization

**Concern:**
- Only 40% went through prior authorization process
- Suggests opportunity for tighter utilization management

---

### 5. Financial Impact Projection

**Current State (No PA):**
- 35 new members × $66,000 annual cost = $2.3M annual impact
- Plus 20% growth trend = $2.8M total impact next year

**With Prior Authorization:**
- Historical PA approval rate: 75% (25% denied or changed to alternative)
- Estimated impact: Prevent 9 inappropriate starts
- Annual savings: 9 members × $66,000 = $594K first year
- Ongoing annual savings: $2.1M (as PA applies to all new starts)

---

## Recommendations

### Primary Recommendation: Implement Prior Authorization for ADALIMUMAB

**Rationale:**
- Appropriate utilization management for $66K/year drug
- Industry standard practice
- 25% of cases can be managed with lower-cost alternatives
- Does not deny access to patients who truly need it

**Implementation Plan:**
1. **Month 1:** Develop PA criteria with medical director
   - Diagnosis requirements
   - Step therapy protocol (try conventional DMARDs first)
   - Documentation requirements

2. **Month 2:** Physician education and communication
   - Notify prescribers of new policy
   - Provide criteria and submission process
   - Offer clinical consultation support

3. **Month 3:** Go-live with PA requirement
   - 48-hour turnaround on requests
   - Pharmacist-led review with physician oversight
   - Track approval rates and denial reasons

4. **Month 4+:** Monitor and refine
   - Track clinical outcomes
   - Measure turnaround times
   - Adjust criteria based on real-world experience

**Expected Outcomes:**
- **First Year Savings:** $594K
- **Ongoing Annual Savings:** $2.1M
- **Quality Impact:** Neutral to positive (ensures right drug, right patient)
- **Administrative Cost:** $180K annually (pharmacist review time)
- **Net Savings:** $1.9M annually

---

### Secondary Recommendation: Biosimilar Adoption Initiative

**Context:** 
- ADALIMUMAB has biosimilar alternatives available
- Biosimilars cost 20-30% less than reference product
- Clinical studies show equivalent efficacy and safety

**Opportunity:**
- Current 823 members on ADALIMUMAB
- Average annual cost: $66,000
- Biosimilar cost: ~$46,000 (30% discount)
- Potential savings: 823 × $20,000 = $16.5M annually (if 100% adoption)

**Realistic Implementation:**
- Year 1: New starts only → 35 members → $700K savings
- Year 2: Add voluntary switches → 200 members → $4M total savings  
- Year 3: Formulary preference for biosimilar → 600 members → $12M total savings

**Action Steps:**
1. Add biosimilar to formulary (same tier as reference product)
2. Default new prescriptions to biosimilar
3. Physician education on biosimilar equivalence
4. Voluntary switch program with incentives
5. Eventually prefer biosimilar over reference product

---

### Tertiary Recommendation: Enhanced Specialty Pharmacy Program

**Opportunity:**
- Improve medication adherence and outcomes
- Reduce waste from unfilled or abandoned prescriptions
- Better patient support = better results

**Program Components:**
1. **Patient Education:** Phone counseling before first fill
2. **Side Effect Management:** Proactive monitoring and intervention
3. **Financial Assistance:** Help patients access manufacturer copay programs
4. **Adherence Support:** Refill reminders and coordination
5. **Outcomes Tracking:** Monitor lab values and clinical response

**Expected Impact:**
- Improve adherence from 85% to 92% → Better health outcomes
- Reduce abandonment from 8% to 3% → Prevent wasted PAs and physician time
- Patient satisfaction scores increase
- Cost: $500 per member per year
- Value: Improved outcomes + reduced medical costs (hospitalizations prevented)

---

## Conclusion

The 18% increase in specialty drug costs is driven by appropriate, clinically necessary 
utilization growth. However, there are significant opportunities for management:

1. **Short-term (0-6 months):** Implement prior authorization → $2.1M annual savings
2. **Medium-term (6-18 months):** Drive biosimilar adoption → $4M additional savings  
3. **Long-term (18+ months):** Enhanced specialty program → Better outcomes + $12M+ savings

**Total Opportunity:** $18M+ annual savings while maintaining or improving quality of care.

---

*This type of analysis is what PharmEngine AI can generate automatically through 
conversational queries like: "Why did specialty costs increase in Q4 and what should we do about it?"*
"""

# ============================================
# UPLOAD TO GCS
# ============================================
def upload_document(content, filename):
    """Upload document to GCS"""
    blob = bucket.blob(filename)
    blob.upload_from_string(content, content_type='text/markdown')
    print(f"✓ Uploaded: {filename} ({len(content):,} characters)")

try:
    print("\n📤 Uploading documents to Cloud Storage...\n")
    
    upload_document(data_dictionary, 'data_dictionary.md')
    upload_document(business_glossary, 'business_glossary.md')
    upload_document(example_analysis, 'example_analysis.md')
    
    print("\n" + "="*60)
    print("✅ DOCUMENTATION UPLOAD COMPLETE!")
    print("="*60)
    print(f"\n📚 Documents in bucket: gs://{BUCKET_NAME}/")
    print("  • data_dictionary.md")
    print("  • business_glossary.md")
    print("  • example_analysis.md")
    print(f"\n🔗 View in Console:")
    print(f"  https://console.cloud.google.com/storage/browser/{BUCKET_NAME}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    raise