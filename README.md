# PharmEngine AI 🏥
   
   **Conversational Analytics Platform for Pharmacy Data**
   
   An agentic AI system that autonomously analyzes pharmacy claims data, generates insights, and provides actionable recommendations for healthcare business decisions.
   
   ## 🚀 Features
   
   - **Conversational Analytics**: Natural language interface to query pharmacy data
   - **Agentic AI**: Autonomous multi-step reasoning and tool orchestration
   - **BigQuery Integration**: Direct queries to enterprise data warehouse
   - **RAG System**: Retrieves business context from documentation
   - **Decision Intelligence**: Generates actionable recommendations with business impact
   - **Production-Ready**: Deployed on GCP with monitoring and observability
   
   ## 🏗️ Architecture
```
   Streamlit UI
       ↓
   LangGraph Agent
       ↓
   Tools:
   ├── BigQuery SQL Tool
   ├── Statistical Analysis Tool
   ├── Documentation RAG
   └── Recommendation Engine
       ↓
   Data Sources:
   ├── BigQuery (Claims Data)
   └── GCS (Documentation)
```
   
   ## 🛠️ Tech Stack
   
   - **Cloud Platform**: Google Cloud Platform (GCP)
   - **Data Warehouse**: BigQuery
   - **LLM**: Vertex AI (Gemini Pro)
   - **Agent Framework**: LangGraph
   - **Vector Store**: ChromaDB
   - **UI**: Streamlit
   - **Deployment**: Cloud Run
   
   ## 📊 Dataset
   
   Synthetic pharmacy claims data including:
   - 50,000+ prescription claims
   - 10,000+ member demographics
   - Drug formulary information
   - Realistic healthcare patterns
   
   ## 🔧 Setup
   
   See `docs/setup.md` for detailed setup instructions.
   
   ## 📈 Key Metrics
   
   - Generic Dispensing Rate (GDR)
   - Per Member Per Month Cost (PMPM)
   - Specialty Drug Proportion
   - Medication Adherence Rates
   
   ## 🎯 Business Use Cases
   
   1. Utilization trend analysis
   2. Cost driver identification
   3. Formulary optimization
   4. Member risk stratification
   5. Clinical program targeting
   
   ## 📝 License
   
   This is a portfolio project for demonstration purposes.
   
   ---
   
   **Project ID**: pharmengine-ai
   **Built with**: LangGraph, Vertex AI, BigQuery, Streamlit