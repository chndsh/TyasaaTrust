# TyasaaTrust
# Alt Trust Layer — Repo Guide
### For all three team members

---

## Repo structure

This is everything that should exist in the repository after the first setup.
If a file is missing, do not create it in the wrong place.

```
alt-trust-layer/                   ← root of the repo
│
├── docker-compose.yml             ← starts ALL services with one command
├── requirements.txt               ← all Python packages (backend + frontend)
├── .env                           ← your secrets (never commit this)
├── .env.example                   ← template — commit this, not .env
├── .gitignore
│
├── backend/                       ← FastAPI + Celery
│   ├── main.py                    ← FastAPI app entry point
│   ├── tasks.py                   ← Celery task definitions
│   ├── models.py                  ← SQLAlchemy table models
│   ├── db/
│   │   └── init.sql               ← schema, runs automatically on first boot
│   ├── modules/
│   │   ├── social_graph.py        ← Person A owns this
│   │   ├── psychometric.py        ← Person B owns this
│   │   ├── behavioral.py          ← Person C owns this
│   │   └── fusion.py              ← Person C owns this
│   ├── routers/
│   │   ├── graph.py               ← Person A owns this
│   │   ├── psych.py               ← Person B owns this
│   │   ├── ingest.py              ← Person C owns this
│   │   └── scoring.py             ← Person C owns this
│   └── data/
│       ├── questions.py           ← Person B owns this
│       └── mock_generator.py      ← Person C owns this
│
└── frontend/                      ← Streamlit
    ├── app.py                     ← main page (landing / home)
    └── pages/
        ├── 2_graph_explorer.py    ← Person A owns this
        ├── 3_quiz.py              ← Person B owns this
        └── 4_dashboard.py        ← Person C owns this
```

> The `pages/` folder uses number prefixes (`2_`, `3_`, `4_`) because
> Streamlit uses them to set the order in the sidebar automatically.

> **Note:** `requirements.txt` is now consolidated at the root level and includes
> all dependencies for both backend and frontend. The individual `requirements.txt` files
> in `backend/` and `frontend/` folders are no longer used.

---

## Services and ports

When `docker compose up` is running, these are available on your machine:

| Service | URL | What it is |
|---|---|---|
| Streamlit UI | http://localhost:8501 | The merchant-facing app |
| FastAPI docs | http://localhost:8000/docs | Interactive API explorer |
| FastAPI raw | http://localhost:8000 | The backend API |
| PostgreSQL | localhost:5432 | Database (use any DB client) |
| Redis | localhost:6379 | Task queue (no UI needed) |

---

## One-time setup (do this once, together)

### 1. One person creates the GitHub repo and pushes the initial files

```bash
# On the person who received the Docker + requirements files
cd alt-trust-layer

git init
git add .
git commit -m "chore: initial project setup"

# Create a new repo on GitHub (do NOT initialise with README)
git remote add origin https://github.com/<your-org>/alt-trust-layer.git
git branch -M main
git push -u origin main
```

### 2. The other two people clone it

```bash
git clone https://github.com/<your-org>/alt-trust-layer.git
cd alt-trust-layer
```

### 3. Everyone creates their `.env` file

The `.env` file is never in the repo (it is in `.gitignore`).
Each person creates their own copy:

```bash
cp .env.example .env
```

Then open `.env` and fill in your Gemini API key:

```
GEMINI_API_KEY=paste_your_actual_key_here
```

Everything else in `.env` can stay as the default values.

### 4. Start the project

```bash
docker compose up
```

The first run takes 3–5 minutes — it is downloading the Python image and
installing all packages. Every run after that is faster.

You will know it is ready when you see this in the terminal:

```
atl_backend   | INFO:     Application startup complete.
atl_frontend  | You can now view your Streamlit app in your browser.
```

---

## Daily workflow — how to start each day

```bash
# 1. Pull any changes your teammates pushed overnight
git pull origin main

# 2. Start all services in the background
docker compose up -d

# 3. Watch the logs to make sure nothing is broken
docker compose logs -f backend
# Press Ctrl+C to stop watching logs — services keep running in background
```

---

## Making changes to code

The `backend/` and `frontend/` folders are mounted as live volumes inside Docker.
This means **you do not need to restart Docker when you save a file** — changes
appear immediately.

- FastAPI reloads automatically on save (the `--reload` flag is set).
- Streamlit reloads automatically on save (the `--server.runOnSave` flag is set).

The only time you need to restart is when you change `requirements.txt`
(adding a new package). In that case:

```bash
docker compose down
docker compose up
```

---

## Branch and Git workflow

You each work on your own branch. Never push directly to `main`.

```
main
 ├── dev/person-a-social-graph
 ├── dev/person-b-psychometric
 └── dev/person-c-behavioral-fusion
```

### Creating your branch (do this once)

```bash
# Person A
git checkout -b dev/person-a-social-graph

# Person B
git checkout -b dev/person-b-psychometric

# Person C
git checkout -b dev/person-c-behavioral-fusion
```

### Saving your work (end of each session)

Only add the files you own. Do not `git add .` — that risks overwriting
someone else's work.

```bash
# Person A example
git add backend/modules/social_graph.py
git add backend/routers/graph.py
git add frontend/pages/2_graph_explorer.py
git commit -m "feat: pagerank reputation scoring"
git push origin dev/person-a-social-graph
```

### Merging into main

When a module is working end to end:

1. Go to GitHub → open a Pull Request from your branch into `main`
2. One other team member reviews it (just a quick look)
3. Merge it

### Pulling merged work from teammates

After a teammate merges their branch, get their code:

```bash
git pull origin main
```

You do not need to switch branches. This updates your branch with their merged changes.

---

## Useful commands (reference)

### Docker

```bash
# Start everything (foreground, see all logs)
docker compose up

# Start everything (background, silent)
docker compose up -d

# Stop everything
docker compose down

# Stop and DELETE the database (fresh start)
docker compose down -v

# Rebuild after changing requirements.txt
docker compose up --build

# See logs for one service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f worker
docker compose logs -f postgres

# Open a shell inside the backend container
docker compose exec backend bash

# Open the PostgreSQL command line
docker compose exec postgres psql -U atl_user -d alt_trust
```

### Git

```bash
# See what files you have changed
git status

# See what changed inside a file
git diff backend/modules/social_graph.py

# Undo changes to a file (careful — this is permanent)
git checkout -- backend/modules/social_graph.py

# See commit history
git log --oneline

# Pull latest from main without switching branch
git pull origin main
```

### Running scripts inside Docker

```bash
# Seed the database with mock data (Person C sets this up)
docker compose exec backend python data/mock_generator.py

# Run a quick API test from inside the container
docker compose exec backend python -c "
import httpx
r = httpx.get('http://localhost:8000/health')
print(r.json())
"
```

---

## How `main.py` works — the router registration pattern

`backend/main.py` is the FastAPI entry point. Each person's router is commented
out by default. You uncomment your own line when your router is ready.

```python
# main.py

from fastapi import FastAPI

app = FastAPI(title="Alternative Trust Layer API")

@app.get("/health")
async def health():
    return {"status": "ok"}

# Uncomment your line when your router is working:
# from routers.graph   import router as graph_router    ← Person A
# from routers.psych   import router as psych_router    ← Person B
# from routers.ingest  import router as ingest_router   ← Person C
# from routers.scoring import router as scoring_router  ← Person C

# app.include_router(graph_router,   prefix="/graph",   tags=["graph"])
# app.include_router(psych_router,   prefix="/psych",   tags=["psychometric"])
# app.include_router(ingest_router,  prefix="/ingest",  tags=["ingest"])
# app.include_router(scoring_router, prefix="/scores",  tags=["scores"])
```

When you uncomment your lines and save, FastAPI restarts and your endpoints
appear immediately at `http://localhost:8000/docs`.

---

## Connecting frontend to backend

Inside Docker, the frontend container talks to the backend container using
the service name `backend`, not `localhost`. Always use:

```python
API_URL = "http://backend:8000"   # correct — works inside Docker
API_URL = "http://localhost:8000" # wrong — only works outside Docker
```

This is already set via the `API_URL` environment variable in `docker-compose.yml`.
In Streamlit, read it like this:

```python
import os
API = os.getenv("API_URL", "http://backend:8000")
```

---

## Database access

The database schema is created automatically from `backend/db/init.sql`
the first time Docker starts. You never need to run it manually.

To inspect the database directly:

```bash
docker compose exec postgres psql -U atl_user -d alt_trust

# Inside psql:
\dt                          -- list all tables
SELECT * FROM merchants;     -- see all merchants
SELECT * FROM trust_scores ORDER BY scored_at DESC LIMIT 5;
\q                           -- quit
```

If you change `init.sql` (only do this after agreeing with the team),
everyone needs to reset their database:

```bash
docker compose down -v    # deletes all data
docker compose up         # recreates from the updated init.sql
```

---

## Checklist before the demo

Run through this together on the day:

```bash
# 1. Pull the latest merged code
git pull origin main

# 2. Fresh start with clean database
docker compose down -v
docker compose up -d

# 3. Seed mock data
docker compose exec backend python data/mock_generator.py

# 4. Check all services are healthy
docker compose ps

# 5. Hit the full scoring endpoint
docker compose exec backend python -c "
import httpx
r = httpx.get('http://localhost:8000/scores/00000000-0000-0000-0000-000000000001')
import json; print(json.dumps(r.json(), indent=2))
"

# 6. Open the UI
# http://localhost:8501
```

If step 5 returns a JSON object with `final_score`, `social_score`,
`psych_score`, and `behavioral_score` all filled in — you are ready.
