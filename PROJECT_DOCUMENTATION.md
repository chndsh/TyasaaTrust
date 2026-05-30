# TyasaaTrust - Project Documentation

## Overview

**TyasaaTrust** is a trust scoring system built for the JunctionX hackathon (Hi Tech Track). It evaluates merchant trustworthiness by combining multiple assessment dimensions: social graph analysis, psychometric evaluation, and behavioral patterns. The system uses a multi-layered scoring approach to produce a comprehensive trust score.

**Repository:** `chndsh/TyasaaTrust`  
**Language Composition:** Python (94.6%), Dockerfile (5.4%)  
**Description:** JunctionX hackathon: Hi Tech Track

---

## Project Objectives

1. **Multi-Dimensional Trust Assessment** - Create a system that evaluates trust across three independent dimensions:
   - Social Graph Analysis (network reputation and connections)
   - Psychometric Scoring (behavioral traits and personality indicators)
   - Behavioral Signals (digital footprint, transaction patterns, and sentiment)

2. **Modular Architecture** - Design the system so three team members can work independently on separate modules with clear interfaces and shared stubs for parallel development.

3. **Real-Time Scoring** - Provide quick access to composite trust scores via REST APIs and display them through an intuitive web interface.

4. **End-to-End Integration** - Enable seamless data flow from ingestion through individual scoring modules to final fusion and dashboard visualization.

---

## Technology Stack

### Backend
- **FastAPI** (v0.111.0) - REST API framework with automatic documentation
- **Uvicorn** (v0.29.0) - ASGI web server
- **SQLAlchemy** (v2.0.30) + **asyncpg** - Async ORM and PostgreSQL driver
- **Celery** (v5.3.6) + **Redis** (v5.0.4) - Distributed task queue for background jobs
- **NetworkX** (v3.3) - Graph algorithms for social network analysis
- **scikit-learn** (v1.4.2) - Machine learning utilities for scoring
- **Google Generative AI** (v0.5.4) - LLM integration for advanced analysis

### Frontend
- **Streamlit** (v1.35.0) - Rapid web UI framework
- **Plotly** (v5.22.0) - Interactive visualizations

### Infrastructure
- **PostgreSQL 16** (Docker) - Primary data store
- **Redis 7** (Docker) - Task queue and caching
- **Docker & Docker Compose** - Containerization and local development

---

## File Structure and Descriptions

```
TyasaaTrust/
├── docker-compose.yml           # Docker services configuration (PostgreSQL, Redis)
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies (consolidated)
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── README.md                    # Team setup and workflow guide
│
├── backend/                     # FastAPI backend application
│   ├── main.py                  # Entry point; registers all routers
│   ├── tasks.py                 # Celery task definitions
│   ├── models.py                # SQLAlchemy ORM models (placeholder)
│   │
│   ├── db/
│   │   └── init.sql             # Database schema initialization script
│   │
│   ├── modules/                 # Core business logic (scoring algorithms)
│   │   ├── social_graph.py      # Social reputation scoring (stub)
│   │   ├── psychometric.py      # Personality trait assessment
│   │   ├── behavioral.py        # Digital behavior and sentiment analysis
│   │   └── fusion.py            # Score aggregation logic
│   │
│   ├── routers/                 # API endpoint handlers
│   │   ├── graph.py             # Social graph endpoint (GET /graph/{merchant_id})
│   │   ├── psych.py             # Psychometric endpoints (POST /psych/submit, GET /psych/questions)
│   │   ├── ingest.py            # Data ingestion endpoint (POST /ingest/digital-footprint)
│   │   └── scoring.py           # Composite scoring endpoint (GET /scores/{merchant_id})
│   │
│   └── data/
│       ├── questions.py         # Quiz question definitions
│       └── mock_generator.py    # Database seeding utility (stub)
│
└── frontend/                    # Streamlit web application
    ├── app.py                   # Home page / landing page
    └── pages/
        ├── 2_graph_explorer.py  # Social graph visualization interface
        ├── 3_quiz.py            # Psychometric quiz interface
        └── 4_dashboard.py       # Composite trust score dashboard
```

---

## Detailed File Descriptions

### **Root Configuration Files**

#### `docker-compose.yml`
Orchestrates local development infrastructure:
- **PostgreSQL 16**: Database on `localhost:5432`
- **Redis 7**: Cache and task queue on `localhost:6379`
- Includes health checks and persistent volumes for data durability

#### `Dockerfile`
Python 3.11-slim base image with security hardening:
- Installs build dependencies for compiled packages (numpy, psycopg2)
- Runs as unprivileged user (appuser) for security
- Copies requirements and installs all Python dependencies

#### `requirements.txt`
Consolidated dependency list (used by both backend and frontend):
- Web frameworks: FastAPI, Uvicorn, Streamlit
- Database: SQLAlchemy, asyncpg, psycopg2
- Task queue: Celery, Redis
- Data science: NetworkX, scikit-learn, pandas, numpy
- AI: google-generativeai
- Utilities: python-dotenv, pydantic, faker

#### `.env.example`
Template for environment configuration (copy to `.env`):
- Database credentials (PostgreSQL)
- Service URLs (Database, Redis, API)
- API keys (Gemini)

---

### **Backend Core Files**

#### `backend/main.py`
**Purpose:** FastAPI application entry point  
**Functionality:**
- Loads environment variables
- Creates FastAPI app instance
- Registers all routers: graph, psych, ingest, scoring
- Provides health check endpoint (`GET /health`)

**Key Pattern:** Router registration allows independent module development and testing.

#### `backend/tasks.py`
**Purpose:** Celery background task definitions  
**Functionality:**
- Initializes Celery app with Redis broker and backend
- Defines placeholder task (`my_background_task`)
- Ready for async processing of long-running operations

**Use Case:** Score computation, data processing, email notifications

#### `backend/models.py`
**Purpose:** SQLAlchemy ORM model definitions (placeholder)  
**Status:** Currently empty; ready for database schema models

**Expected Content:** Merchant, User, Score, Transaction models

---

### **Backend Modules (Business Logic)**

#### `backend/modules/social_graph.py`
**Purpose:** Social reputation and network analysis  
**Ownership:** Person A  
**Functionality:**
```python
get_social_graph_score(merchant_id: str) -> dict
```
- Returns stub score (0.62) with social connection signals
- Tracks: connection count (18), community score (0.7)
- Ready for graph algorithm replacement (PageRank, centrality measures)

**Dependencies:** NetworkX (for future graph traversal)

#### `backend/modules/psychometric.py`
**Purpose:** Personality trait assessment and quiz scoring  
**Ownership:** Person B  
**Functions:**
```python
score_responses(responses: list[dict]) -> dict
get_psychometric_score(merchant_id: str) -> dict
```
- `score_responses`: Computes personality traits from quiz answers
  - Scoring logic: Base 0.4 + 0.05 per response (capped at 0.95)
  - Returns: Traits (openness, conscientiousness) and summary
- `get_psychometric_score`: Retrieves stored psychometric profile
- Traits tracked: openness (0.6), conscientiousness (0.55)

**Dependencies:** Quiz data from `backend/data/questions.py`

#### `backend/modules/behavioral.py`
**Purpose:** Digital behavior and transaction pattern analysis  
**Ownership:** Person C  
**Functions:**
```python
get_behavioral_score(merchant_id: str) -> dict
summarize_digital_footprint(events: list[dict]) -> dict
```
- `get_behavioral_score`: Aggregates behavior signals
  - Tracks: review sentiment (0.63), chargeback rate (0.04)
  - Base score: 0.6
- `summarize_digital_footprint`: Processes transaction/event stream
  - Counts events and generates summary

**Dependencies:** Event data from ingest router

#### `backend/modules/fusion.py`
**Purpose:** Score aggregation and final trust computation  
**Ownership:** Person C  
**Functions:**
```python
combine_scores(merchant_id: str, social: dict, psych: dict, behavioral: dict) -> dict
```
- Averages three sub-scores: (social + psych + behavioral) / 3
- Returns comprehensive scoring object with all components
- Enables transparency into score composition

---

### **Backend Routers (API Endpoints)**

#### `backend/routers/graph.py`
**Purpose:** Social graph API endpoint  
**Ownership:** Person A  
**Endpoints:**
```
GET /graph/{merchant_id}
```
Returns: Social score, connection signals, community metrics

#### `backend/routers/psych.py`
**Purpose:** Psychometric assessment endpoints  
**Ownership:** Person B  
**Endpoints:**
```
GET /psych/questions      # Fetch quiz questions
POST /psych/submit        # Submit quiz responses and get scoring
```

**Request Schema (POST /psych/submit):**
```json
{
  "merchant_id": "string",
  "responses": [
    {"question": "str", "answer": "str", "trait": "str"}
  ]
}
```

#### `backend/routers/ingest.py`
**Purpose:** Data ingestion and behavioral signal collection  
**Ownership:** Person C  
**Endpoints:**
```
POST /ingest/digital-footprint
```

**Request Schema:**
```json
{
  "merchant_id": "string",
  "events": [{"type": "transaction", "value": 100}, ...]
}
```

#### `backend/routers/scoring.py`
**Purpose:** Composite trust score orchestration  
**Ownership:** Person C  
**Endpoints:**
```
GET /scores/{merchant_id}
```

**Workflow:**
1. Calls `get_social_graph_score(merchant_id)`
2. Calls `get_psychometric_score(merchant_id)`
3. Calls `get_behavioral_score(merchant_id)`
4. Passes all three to `combine_scores()` for fusion
5. Returns aggregated result with all component scores

---

### **Backend Data Files**

#### `backend/data/questions.py`
**Purpose:** Quiz question definitions  
**Ownership:** Person B  
**Content:**
```python
QUESTIONS = [
  {
    "question": "How often do you validate customer identity...",
    "trait": "conscientiousness",
    "options": ["Always", "Often", "Sometimes", "Rarely"]
  },
  ...
]
```

**Used By:** `routers/psych.py` → Frontend quiz UI

#### `backend/data/mock_generator.py`
**Purpose:** Database seed data generator  
**Ownership:** Person C  
**Status:** Stub (placeholder for seed logic)
**Use:** `python backend/data/mock_generator.py` during development

---

### **Backend Database**

#### `backend/db/init.sql`
**Purpose:** PostgreSQL schema initialization  
**Status:** Currently empty placeholder
**Expected Content:**
- Merchant table (id, name, created_at)
- Score records (merchant_id, component scores, timestamp)
- Quiz responses (merchant_id, question_id, answer, trait)
- Digital events (merchant_id, event_type, timestamp, metadata)

**Behavior:** Automatically executed on Docker Compose startup

---

### **Frontend Files**

#### `frontend/app.py`
**Purpose:** Streamlit home page and navigation hub  
**Functionality:**
- Sets page config (title, layout)
- Displays welcome message
- Shows backend API URL for debugging
- Sidebar automatically links to numbered pages (2_*, 3_*, 4_*)

**Output:** http://localhost:8501 (after `streamlit run app.py --server.port 8501`)

#### `frontend/pages/2_graph_explorer.py`
**Purpose:** Social graph visualization and exploration  
**Ownership:** Person A  
**UI Components:**
- Text input for merchant_id
- Button to fetch social score
- JSON display of response

**API Call:**
```python
GET {API_URL}/graph/{merchant_id}
```

**Error Handling:** Gracefully catches backend connection failures

#### `frontend/pages/3_quiz.py`
**Purpose:** Interactive psychometric quiz interface  
**Ownership:** Person B  
**Workflow:**
1. Fetches question list from `GET /psych/questions`
2. Renders radio buttons for each question
3. Collects user responses
4. On submit: POSTs to `/psych/submit` with merchant_id and responses
5. Displays scoring results (traits, summary)

**State Management:** Uses Streamlit's session state for form persistence

#### `frontend/pages/4_dashboard.py`
**Purpose:** Composite trust score dashboard and metrics  
**Ownership:** Person C  
**Functionality:**
- Text input for merchant_id
- Refresh button to fetch latest scores
- Displays four metrics:
  - Final score (averaged composite)
  - Social score component
  - Psych score component
  - Behavioral score component
- Raw JSON response display

**API Call:**
```python
GET {API_URL}/scores/{merchant_id}
```

---

## How Files Work Together

### **Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  app.py (hub)                                                    │
│    ├→ 2_graph_explorer.py → GET /graph/{id}                    │
│    ├→ 3_quiz.py           → GET/POST /psych/*                  │
│    └→ 4_dashboard.py      → GET /scores/{id}                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓ HTTP Calls                     ↑ JSON Responses
┌─────────────────────────────────────────────────────────────────┐
│           Backend API (FastAPI) - main.py                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Routers Registration:                                           │
│  ├─ /graph       → routers/graph.py      ──→ modules/           │
│  ├─ /psych       → routers/psych.py      ──→ modules/           │
│  ├─ /ingest      → routers/ingest.py     ──→ modules/           │
│  └─ /scores      → routers/scoring.py    ──→ modules/           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓ Function Calls
┌─────────────────────────────────────────────────────────────────┐
│              Business Logic Modules                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  social_graph.py ──→ [Graph Algorithm] ──→ Social Score         │
│  psychometric.py ──→ [Trait Scoring]   ──→ Psych Score          │
│  behavioral.py   ──→ [Pattern Analysis] ──→ Behavioral Score   │
│                              ↓                                    │
│  fusion.py ──→ [Average Scores] ──→ Final Score (0-1)           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         ↓ Data Storage (Optional)
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL Database          │  Redis Cache / Task Queue        │
│  ├─ merchants                 │  ├─ Score cache                 │
│  ├─ scores                    │  ├─ Session data                │
│  ├─ quiz_responses            │  └─ Celery tasks                │
│  └─ digital_events            │                                  │
└─────────────────────────────────────────────────────────────────┘
```

### **Request Flow Example: Get Complete Trust Score**

**User Action:** Click "Refresh scores" on Dashboard (4_dashboard.py)

```
1. Frontend (4_dashboard.py):
   GET http://localhost:8000/scores/merchant-demo
   
2. Backend Router (routers/scoring.py):
   score_merchant("merchant-demo")
   
3. Orchestration:
   ├─ Call modules.social_graph.get_social_graph_score("merchant-demo")
   │  └─ Returns: {"social_score": 0.62, "signals": {...}}
   │
   ├─ Call modules.psychometric.get_psychometric_score("merchant-demo")
   │  └─ Returns: {"psych_score": 0.57, "traits": {...}}
   │
   ├─ Call modules.behavioral.get_behavioral_score("merchant-demo")
   │  └─ Returns: {"behavioral_score": 0.6, "signals": {...}}
   │
   └─ Call modules.fusion.combine_scores(
       "merchant-demo", social, psych, behavioral
     )
        └─ Computes: (0.62 + 0.57 + 0.6) / 3 = 0.597
        └─ Returns aggregated result
        
4. HTTP Response (JSON):
   {
     "merchant_id": "merchant-demo",
     "final_score": 0.597,
     "social_score": 0.62,
     "psych_score": 0.57,
     "behavioral_score": 0.6,
     "status": "stub"
   }

5. Frontend Display:
   Dashboard shows all metrics with Streamlit components
```

### **Quiz Submission Flow**

**User Action:** Complete quiz and submit on 3_quiz.py

```
1. Frontend (3_quiz.py):
   - Fetches questions: GET /psych/questions
   - User selects answers
   - POST /psych/submit with:
     {
       "merchant_id": "user-123",
       "responses": [
         {"question": "...", "answer": "Always", "trait": "conscientiousness"},
         {"question": "...", "answer": "Very comfortable", "trait": "openness"}
       ]
     }

2. Backend Router (routers/psych.py):
   submit_quiz(QuizSubmission)
   
3. Module Logic (modules/psychometric.py):
   score_responses(submission.responses)
   - Computes score: 0.4 + (2 * 0.05) = 0.5
   - Extracts traits: openness, conscientiousness
   
4. Response back to Frontend:
   {
     "merchant_id": "user-123",
     "psych_score": 0.5,
     "traits": {"openness": 0.58, "conscientiousness": 0.62},
     "summary": "stubbed from response count"
   }

5. Frontend displays results
```

---

## Development Workflow & Ownership

### **Team Structure**

| Person | Modules | Routers | Frontend |
|--------|---------|---------|----------|
| **A** | social_graph.py | graph.py | 2_graph_explorer.py |
| **B** | psychometric.py | psych.py | 3_quiz.py |
| **C** | behavioral.py + fusion.py | ingest.py + scoring.py | 4_dashboard.py + data/ |

### **Development Process**

1. **Setup** (Once):
   - Clone repo, copy `.env.example` → `.env`
   - Install dependencies: `pip install -r requirements.txt`
   - Start services: `docker compose up -d`

2. **Daily Development**:
   - Each developer works on their own branch: `dev/person-{letter}-{module}`
   - Run locally with hot-reload enabled:
     ```bash
     cd backend && uvicorn main:app --reload --port 8000
     cd frontend && streamlit run app.py --server.port 8501
     ```
   - Stub implementations allow independent testing before merging

3. **Integration**:
   - When module is complete, create Pull Request
   - Peer review before merging to `main`
   - Use `/scores/{merchant_id}` endpoint to verify all components work together

---

## Key Design Patterns

### **1. Router-Module Separation**
- **Routers** (in `routers/`): HTTP layer, validation, serialization
- **Modules** (in `modules/`): Pure business logic, testable, reusable
- **Benefit:** Clear separation of concerns; easy to test modules independently

### **2. Stub Implementation**
- Each module has stub functions returning realistic dummy data
- Enables frontend and API to work before all modules are complete
- Replace stub logic with real algorithms; interface stays the same

### **3. Composition-Based Scoring**
- Three independent scoring systems produce component scores
- `fusion.py` combines them into final score
- Each component is transparent (not a black box)

### **4. Environment-Driven Configuration**
- All URLs, credentials, API keys in `.env`
- Easy to switch between local, staging, production
- Never commit secrets; `.env` is in `.gitignore`

---

## Services and Ports

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit UI** | http://localhost:8501 | Frontend web interface |
| **FastAPI Docs** | http://localhost:8000/docs | Interactive API documentation (Swagger) |
| **FastAPI API** | http://localhost:8000 | Raw API endpoint |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Task queue and cache |

---

## Common Commands

### **Docker**
```bash
docker compose up -d          # Start database + Redis (background)
docker compose down           # Stop services
docker compose down -v        # Stop and delete data (fresh start)
docker compose logs -f postgres
docker compose exec postgres psql -U atl_user -d alt_trust
```

### **Backend**
```bash
cd backend
uvicorn main:app --reload --port 8000    # Run with hot-reload
python -c "import httpx; r = httpx.get('http://localhost:8000/health'); print(r.json())"
```

### **Frontend**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### **Database**
```bash
python backend/data/mock_generator.py    # Seed test data
```

---

## Example End-to-End Test

```bash
# 1. Start infrastructure
docker compose up -d

# 2. In Terminal 1: Start backend
cd backend && uvicorn main:app --reload --port 8000

# 3. In Terminal 2: Start frontend
cd frontend && streamlit run app.py --server.port 8501

# 4. Test via API
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/scores/merchant-123
# {
#   "merchant_id": "merchant-123",
#   "final_score": 0.597,
#   "social_score": 0.62,
#   "psych_score": 0.57,
#   "behavioral_score": 0.6,
#   "status": "stub"
# }

# 5. Open browser to http://localhost:8501
# ✓ All three dashboard pages should display scores
```

---

## Future Enhancements

1. **Real Algorithms**: Replace stub scoring with:
   - PageRank and network centrality for social graphs
   - SHAP values for psychometric interpretation
   - NLP sentiment analysis for behavioral signals

2. **Database Integration**: Persist scores, queries, and audit trails in PostgreSQL

3. **Async Processing**: Use Celery to offload heavy computations (large graph traversal, ML model inference)

4. **Advanced Visualizations**: NetworkX graph rendering, time-series score trends, trait distribution charts

5. **LLM Integration**: Use Google Generative AI to provide narrative explanations of trust scores

6. **Authentication**: Secure endpoints with JWT tokens and role-based access control

---

## Summary

**TyasaaTrust** is a well-structured, modular hackathon project designed for rapid parallel development. It separates concerns into independent modules (social, psychometric, behavioral), exposes them via clean REST APIs, and visualizes results through a Streamlit dashboard. The stub-based architecture allows all three team members to develop simultaneously while maintaining end-to-end system cohesion. The fusion approach produces transparent, multi-dimensional trust scores that users can understand and act upon.

---

## Architectural Decisions: Import Path Resolution

### Problem Statement
The application previously suffered from inconsistent execution boundaries, where executing commands from inside subdirectories caused absolute imports to fail, and root execution caused local subdirectory imports to fail.

### Implemented Solution
1. **Root-Anchored Scoping:** The repository standardizes on **Root Execution**. The root folder `TyasaaTrust/` serves as the primary workspace reference point.
2. **Dynamic Entrypoint Patching:** Critical entrypoints dynamically prepend the absolute path of the workspace to `sys.path` at runtime via `sys.path.insert(0, project_root)`. This ensures that even if a utility script is executed standalone, it retains access to the global `backend` module namespace.
3. **Absolute Package Formatting:** All internal cross-module references must explicitly use the full package path syntax: `from backend.<module>.<submodule> import <component>`.
