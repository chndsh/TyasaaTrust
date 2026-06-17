from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


def get_engine(database_url: str):
    return create_engine(database_url)


def export_table(
    engine,
    table_name: str,
    out_dir: Path,
    sql_query: str | None = None,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    if sql_query is None:
        sql_query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(text(sql_query), engine)
    out_path = out_dir / f"{table_name}.csv"
    df.to_csv(out_path, index=False)
    return out_path


def build_training_csv(
    engine,
    out_dir: Path,
    features_table: str = "behavioral_features",
    scores_table: str = "behavioral_scores",
):
    out_dir.mkdir(parents=True, exist_ok=True)
    # Load features and scores
    feat_q = f"SELECT * FROM {features_table};"
    score_q = f"SELECT * FROM {scores_table};"
    feats = pd.read_sql_query(text(feat_q), engine)
    try:
        scores = pd.read_sql_query(text(score_q), engine)
    except Exception:
        scores = pd.DataFrame()

    feats_path = out_dir / "features.csv"
    feats.to_csv(feats_path, index=False)

    if not scores.empty:
        # join on account_id_hash and as_of_date (if present)
        join_cols = [
            c
            for c in ["account_id_hash", "as_of_date"]
            if c in feats.columns and c in scores.columns
        ]
        if join_cols:
            merged = feats.merge(
                scores[[*join_cols, "score"]], on=join_cols, how="left"
            )
        else:
            # fallback: merge on account_id_hash only
            merged = feats.merge(
                scores[["account_id_hash", "score"]],
                on="account_id_hash",
                how="left",
            )

        train_path = out_dir / "training.csv"
        merged.to_csv(train_path, index=False)
        return feats_path, train_path

    return feats_path, None


def main():
    parser = argparse.ArgumentParser(
        description="Export Postgres tables to CSV for training"
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="Database URL (SQLAlchemy)",
    )
    parser.add_argument(
        "--out-dir",
        default="data/staged/csv",
        help="Output directory for CSVs",
    )
    parser.add_argument(
        "--tables",
        nargs="*",
        default=[
            "utilities_payments",
            "airtime_topups",
            "seasonality_calendar",
            "behavioral_features",
            "behavioral_scores",
        ],
        help="Tables to export",
    )
    args = parser.parse_args()

    if not args.database_url:
        raise RuntimeError(
            "DATABASE_URL is required (set env or pass --database-url)"
        )

    engine = get_engine(args.database_url)
    out_dir = Path(args.out_dir)

    exported = {}
    for t in args.tables:
        try:
            path = export_table(engine, t, out_dir)
            exported[t] = str(path)
        except Exception as e:
            exported[t] = f"error: {e}"

    # Attempt to build training CSV (features + scores)
    try:
        feats_path, train_path = build_training_csv(engine, out_dir)
        exported["features_csv"] = str(feats_path)
        exported["training_csv"] = (
            str(train_path) if train_path is not None else None
        )
    except Exception as e:
        exported["training_csv"] = f"error: {e}"

    print("exported:")
    for k, v in exported.items():
        print(f" - {k}: {v}")


if __name__ == "__main__":
    main()
