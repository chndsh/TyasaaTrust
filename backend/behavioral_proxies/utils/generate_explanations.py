from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd

from ..evaluation.explain import generate_shap_explanations, explanations_to_json


def main():
    parser = argparse.ArgumentParser(description="Generate SHAP explanations for model and feature CSV")
    parser.add_argument("--model-path", required=True, help="Pickle path to trained model")
    parser.add_argument("--features-csv", required=True, help="CSV file with feature rows (account_id_hash + features)")
    parser.add_argument("--out-json", default="data/staged/explanations.json", help="Output JSON path")
    parser.add_argument("--top-k", type=int, default=5, help="Top K features to include")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    features_path = Path(args.features_csv)
    out_path = Path(args.out_json)

    with model_path.open("rb") as fh:
        model = pickle.load(fh)

    df = pd.read_csv(features_path)
    explanations = generate_shap_explanations(model, df, top_k=args.top_k)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    explanations_to_json(explanations, out_path)
    print(f"Wrote explanations to {out_path}")


if __name__ == "__main__":
    main()
