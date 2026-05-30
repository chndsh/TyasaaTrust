import os
import sys

# Compute the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dotenv import load_dotenv
from fastapi import FastAPI

from backend.routers.graph import router as graph_router
from backend.routers.psych import router as psych_router
from backend.routers.ingest import router as ingest_router
from backend.routers.scoring import router as scoring_router

load_dotenv()

app = FastAPI(title="Tyasaa Trust API")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graph_router, prefix="/graph", tags=["graph"])
app.include_router(psych_router, prefix="/psych", tags=["psychometric"])
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(scoring_router, prefix="/scores", tags=["scores"])
