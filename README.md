# Hospital System Chatbot
Source - [RealPython](https://realpython.com/build-llm-rag-chatbot-with-langchain/)

A multi-service RAG (Retrieval-Augmented Generation) chatbot system designed to answer questions about a synthetic hospital network. The system combines structured graph data (Neo4j) with unstructured patient reviews, using LangChain agents and GigaChat LLM for natural language querying.

## 🏥 Overview

This project provides an intelligent chatbot that can answer complex questions about:
- **Hospitals** - Locations, names, and statistics
- **Patients** - Demographics, visits, and medical history
- **Physicians** - Treatments, salaries, and performance metrics
- **Insurance Payers** - Billing amounts and coverage details
- **Patient Reviews** - Sentiment analysis and qualitative feedback
- **Wait Times** - Current hospital availability

The system uses a hybrid approach:
1. **Graph RAG** - Neo4j graph database for structured relationships
2. **Vector RAG** - Semantic search over patient reviews
3. **Live Tools** - Real-time wait time queries

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Chatbot Frontend  │────▶│    Chatbot API      │────▶│  Hospital Neo4j ETL │
│   (Streamlit:8501)  │     │   (FastAPI:8000)    │     │   (Data Loading)    │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                                           │
                                                           ▼
                                                   ┌─────────────────┐
                                                   │   Neo4j Graph   │
                                                   │    Database     │
                                                   └─────────────────┘
```

### Components

#### 1. Hospital Neo4j ETL (`hospital_neo4j_etl/`)
Loads synthetic hospital data from CSV files into Neo4j graph database:
- Creates nodes: Hospital, Patient, Physician, Payer, Visit, Review
- Establishes relationships: AT, WRITES, TREATS, COVERED_BY, HAS, EMPLOYS
- Builds vector indexes for semantic search on reviews

#### 2. Chatbot API (`chatbot_api/`)
FastAPI backend exposing RAG agent endpoints:
- `/hospital-rag-agent` - POST endpoint for natural language queries
- Uses LangChain agents with multiple tools:
  - `graph` - Cypher queries for structured data
  - `experiences` - Vector search for patient reviews
  - `waits` - Current wait times at hospitals
  - `availability` - Find hospital with shortest wait

#### 3. Chatbot Frontend (`chatbot_frontend/`)
Streamlit web interface for interacting with the chatbot:
- Chat history within session
- Example questions sidebar
- Real-time API status checking

## 📁 Data Files

Located in `data/`:
- `hospitals.csv` - Hospital IDs, names, states
- `patients.csv` - Patient demographics
- `physicians.csv` - Physician details and salaries
- `payers.csv` - Insurance companies
- `visits.csv` - Hospital visits with diagnoses, treatments, billing
- `reviews.csv` - Patient reviews linked to visits

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Neo4j database instance (AuraDB or self-hosted)
- GigaChat API credentials

### Environment Configuration

Create a `.env` file in the root directory:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://your-neo4j-host:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# GigaChat LLM Configuration
LLM_API=your_gigachat_api_key
HOSPITAL_QA_MODEL=GigaChat-Pro

# CSV File Paths (for ETL service)
HOSPITALS_CSV_PATH=/app/data/hospitals.csv
PAYERS_CSV_PATH=/app/data/payers.csv
PHYSICIANS_CSV_PATH=/app/data/physicians.csv
PATIENTS_CSV_PATH=/app/data/patients.csv
VISITS_CSV_PATH=/app/data/visits.csv
REVIEWS_CSV_PATH=/app/data/reviews.csv

# Optional Settings
CYPHER_DANGEROUS_REQUESTS=False
DEBUG_API=False
CHATBOT_URL=http://chatbot_api:8000/hospital-rag-agent
```

### Running with Docker Compose

```bash
# Build and start all services
docker compose up --build

# Access the frontend at http://localhost:8501
# API available at http://localhost:8000
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run ETL to load data into Neo4j
cd hospital_neo4j_etl/src
python hospital_bulk_csv_write.py

# Start the API
cd ../chatbot_api/src
uvicorn main:app --host 0.0.0.0 --port 8000

# Start the frontend (in another terminal)
cd ../chatbot_frontend/src
streamlit run main.py
```

## 💬 Example Questions

The chatbot can answer various types of questions:

### Structural Queries
- "Which hospitals are in the hospital system?"
- "What is the ID for physician James Cooper?"

### Wait Time Queries
- "What is the current wait time at Wallace-Hamilton hospital?"
- "Which hospital has the shortest wait time right now?"

### Review Analysis
- "What are patients saying about the nursing staff at Castaneda-Hardy?"
- "How many reviews have been written from patients in Florida?"

### Multi-hop Reasoning
- "At which hospitals are patients complaining about billing and insurance issues?"
- "Which state had the largest percent increase in Medicaid visits from 2022 to 2023?"

## 🛠️ Utilities

### Connection Testing

```bash
# Test Neo4j connectivity
python utils/check_connect_neo4j.py

# Test GigaChat connectivity
python utils/check_connect_gigachat.py
```

### Test Scripts

```bash
# Synchronous API tests
python tests/sync_agent_requests.py

# Asynchronous API tests
python tests/async_agent_requests.py
```

## 📊 Graph Schema

```
(Hospital)-[:EMPLOYS]->(Physician)
    ^                        |
    |                        v
(Visit)-[:AT]--------------->|
    |                        |
    |                        v
    +----[:COVERED_BY]--->(Payer)
    |
    +----[:HAS]--------->(Patient)
    |
    +----[:WRITES]------>(Review)
```

## ⚙️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `CYPHER_DANGEROUS_REQUESTS` | Allow potentially destructive Cypher queries | `False` |
| `DEBUG_API` | Enable debug mode with test API endpoint | `False` |
| `BATCH` | Max documents per embedding batch | `128` |
| `DOCUMENTS_TO_RETURN` | Reviews returned from vector search | `12` |

## 🧪 Testing

Run the included test scripts to verify functionality:

```bash
# Test with sample queries
python tests/sync_agent_requests.py

# Test async performance
python tests/async_agent_requests.py
```

## 📝 Project Structure

```
.
├── chatbot_api/              # FastAPI backend
│   ├── src/
│   │   ├── agents/           # LangChain agent definition
│   │   ├── chains/           # RAG chains (Cypher & Vector)
│   │   ├── models/           # Pydantic models
│   │   ├── tools/            # Custom agent tools
│   │   ├── utils/            # Utility functions
│   │   ├── config.py         # Configuration & connections
│   │   └── main.py           # API entrypoint
│   └── Dockerfile
├── chatbot_frontend/         # Streamlit UI
│   ├── src/
│   │   └── main.py          # Frontend application
│   └── Dockerfile
├── hospital_neo4j_etl/       # Data loading service
│   ├── src/
│   │   ├── config.py        # ETL configuration
│   │   └── hospital_bulk_csv_write.py  # ETL logic
│   └── Dockerfile
├── data/                     # CSV data files
├── tests/                    # Test scripts
├── utils/                    # Utility scripts
├── docker-compose.yml        # Service orchestration
└── requirements.txt          # Python dependencies
```
