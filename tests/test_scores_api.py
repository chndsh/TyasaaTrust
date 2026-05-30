import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.behavioral_proxies.utils.persistence import (  # noqa: E402
    build_database_engine,
    metadata,
)
from backend.main import app  # noqa: E402


def test_write_behavioral_score_endpoint(tmp_path, monkeypatch):
    db_path = tmp_path / "scores.db"
    database_url = f"sqlite+pysqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)

    engine = build_database_engine(database_url)
    metadata.create_all(engine)

    client = TestClient(app)
    response = client.post(
        "/scores/behavioral",
        json={
            "account_id_hash": "hash-123",
            "as_of_date": "2024-05-01",
            "score": 0.7345,
            "model_version": "test-v1",
            "score_details": {"behavioral": 0.8, "psych": 0.6},
        },
    )

    assert response.status_code == 201
    assert response.json() == {"status": "ok", "inserted": 1}

    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT account_id_hash, as_of_date, score, model_version "
                "FROM behavioral_scores"
            )
        ).mappings().one()

    assert row["account_id_hash"] == "hash-123"
    assert str(row["as_of_date"]) == "2024-05-01"
    assert float(row["score"]) == 0.7345
    assert row["model_version"] == "test-v1"
