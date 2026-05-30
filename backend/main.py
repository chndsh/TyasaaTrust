try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv():
        return None

from fastapi import FastAPI

from .routers.graph import router as graph_router
from .routers.psych import router as psych_router
from .routers.ingest import router as ingest_router
from .routers.scoring import router as scoring_router

load_dotenv()

app = FastAPI(title="Tyasaa Trust API")


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(graph_router, prefix="/graph", tags=["graph"])
app.include_router(psych_router, prefix="/psych", tags=["psychometric"])
app.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
app.include_router(scoring_router, prefix="/scores", tags=["scores"])
