# TyasaaTrust
# TyasaaTrust — Repo Guide
### For all three team members

---

## Repo structure

This is everything that should exist in the repository after the first setup.
If a file is missing, do not create it in the wrong place.

```
TyasaaTrust/                       ← root of the repo
│
├── docker-compose.yml             ← starts databases/servers only
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
| Streamlit UI | http://localhost:8501 | Run locally via Streamlit |
| FastAPI docs | http://localhost:8000/docs | Run locally via Uvicorn |
| FastAPI raw | http://localhost:8000 | Run locally via Uvicorn |
| PostgreSQL | localhost:5432 | Database (Docker Compose) |
| Redis | localhost:6379 | Task queue (Docker Compose) |

---

## One-time setup (do this once, together)

### 1. One person creates the GitHub repo and pushes the initial files

```bash
# On the person who received the Docker + requirements files
cd TyasaaTrust

git init
git add .
git commit -m "chore: initial project setup"

# Create a new repo on GitHub (do NOT initialise with README)
git remote add origin https://github.com/<your-org>/TyasaaTrust.git
git branch -M main
git push -u origin main
```

### 2. The other two people clone it

```bash
git clone https://github.com/<your-org>/TyasaaTrust.git
cd TyasaaTrust
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

### 4. Start dependencies + run services locally

```bash
# Create a virtualenv (once)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start database + redis
docker compose up -d

# Terminal 1: backend (run from repo root)
uvicorn backend.main:app --reload --port 8000

# Terminal 2: frontend (run from repo root)
streamlit run frontend/app.py --server.port 8501
```

The first run after installing dependencies takes a bit longer; after that it is instant.

---

## Daily workflow — how to start each day

```bash
# 1. Pull any changes your teammates pushed overnight
git pull origin main

# 2. Start database + redis
docker compose up -d

# 3. Run backend + frontend locally (two terminals, from repo root)
uvicorn backend.main:app --reload --port 8000

# In another terminal
streamlit run frontend/app.py --server.port 8501
```

---

## Making changes to code

The backend and frontend run locally with hot-reload enabled:

- FastAPI reloads automatically on save (the `--reload` flag is set).
- Streamlit reloads automatically on save.

If you change `requirements.txt`, reinstall dependencies and restart the
backend/frontend processes:

```bash
pip install -r requirements.txt
```

---

## Independent development stubs

Each module ships with placeholder outputs so the API and UI can run end-to-end
while each person builds their own portion. Replace the stubbed logic in your
module and router as your feature matures.

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
# Start database + redis (foreground, see logs)
docker compose up

# Start database + redis (background)
docker compose up -d

# Stop database + redis
docker compose down

# Stop and DELETE the database (fresh start)
docker compose down -v

# See logs for one service
docker compose logs -f postgres
docker compose logs -f redis

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

### Running scripts locally

```bash
# Seed the database with mock data (Person C sets this up)
python backend/data/mock_generator.py

# Run a quick API test
python -c "
import httpx
r = httpx.get('http://localhost:8000/health')
print(r.json())
"
```

---

## How `main.py` works — the router registration pattern

`backend/main.py` is the FastAPI entry point. All routers are registered by
default so each person can develop and test independently with stubbed data.
Update your own router/module as you build out your feature.

---

## Connecting frontend to backend

The frontend now runs locally and talks to the local backend:

```python
API_URL = "http://localhost:8000"
```

You can override this via the `API_URL` environment variable (see `.env.example`).

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
python backend/data/mock_generator.py

# 4. Check all services are healthy
docker compose ps

# 5. Hit the full scoring endpoint
python -c "
import httpx
r = httpx.get('http://localhost:8000/scores/00000000-0000-0000-0000-000000000001')
import json; print(json.dumps(r.json(), indent=2))
"

# 6. Open the UI
# http://localhost:8501
```

If step 5 returns a JSON object with `final_score`, `social_score`,
`psych_score`, and `behavioral_score` all filled in — you are ready.

---

## Development & Execution Standard

All components of this repository must be executed from the **repository root directory** (`TyasaaTrust/`). Never change directories into `backend/` to run development servers, tasks, or utilities.

### Local Server Execution
```bash
# 1. Ensure you are in the repository root directory
cd /path/to/TyasaaTrust

# 2. Activate your virtual environment
source venv/bin/activate

# 3. Spin up the ASGI server using the root-relative module path
uvicorn backend.main:app --reload --port 8000
```
