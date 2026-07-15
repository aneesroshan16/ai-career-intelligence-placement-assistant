"""
Placement prediction training pipeline.

Run standalone:
    python -m app.ml_core.placement_model.train --data data/placement_training.csv

Trains RandomForest, XGBoost, and CatBoost candidates, evaluates via
stratified 5-fold CV (ROC-AUC as primary metric), and persists the winner
as `ml_core/artifacts/placement_model_v{n}.pkl` (or `.cbm` for CatBoost)
alongside a `metadata.json` describing feature order, metrics, and version —
consumed at inference time by `registry.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
from datetime import datetime, timezone

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from app.ml_core.placement_model.features import FEATURE_ORDER

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def _evaluate(model, X, y) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    proba = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    preds = (proba >= 0.5).astype(int)
    return {
        "roc_auc": round(roc_auc_score(y, proba), 4),
        "f1": round(f1_score(y, preds), 4),
        "precision": round(precision_score(y, preds), 4),
        "recall": round(recall_score(y, preds), 4),
    }


def train(data_path: str) -> None:
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    df = pd.read_csv(data_path)

    missing = [c for c in FEATURE_ORDER if c not in df.columns]
    if missing:
        raise ValueError(f"Training data missing required columns: {missing}")
    if "placed" not in df.columns:
        raise ValueError("Training data must contain a 'placed' (0/1) label column")

    X = df[FEATURE_ORDER]
    y = df["placed"]

    candidates = {
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=3, random_state=42, n_jobs=-1
        ),
    }
    try:
        from xgboost import XGBClassifier

        candidates["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            eval_metric="logloss", random_state=42, n_jobs=-1,
        )
    except ImportError:
        print("xgboost not installed — skipping candidate")
    try:
        from catboost import CatBoostClassifier

        candidates["catboost"] = CatBoostClassifier(
            iterations=300, depth=5, learning_rate=0.05, verbose=False, random_state=42
        )
    except ImportError:
        print("catboost not installed — skipping candidate")

    results = {}
    for name, model in candidates.items():
        print(f"Evaluating {name}...")
        results[name] = _evaluate(model, X, y)
        print(f"  -> {results[name]}")

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    best_model = candidates[best_name]
    best_model.fit(X, y)
    print(f"\nBest model: {best_name} (ROC-AUC={results[best_name]['roc_auc']})")

    existing = [f for f in os.listdir(ARTIFACT_DIR) if f.startswith("placement_model_v")]
    version = len(existing) + 1
    ext = "cbm" if best_name == "catboost" else "pkl"
    model_filename = f"placement_model_v{version}.{ext}"
    model_path = os.path.join(ARTIFACT_DIR, model_filename)

    if best_name == "catboost":
        best_model.save_model(model_path)
    else:
        with open(model_path, "wb") as f:
            pickle.dump(best_model, f)

    metadata = {
        "version": version,
        "model_type": best_name,
        "model_filename": model_filename,
        "feature_order": FEATURE_ORDER,
        "metrics": {k: v for k, v in results.items()},
        "selected_metrics": results[best_name],
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git_commit(),
        "training_rows": len(df),
    }
    with open(os.path.join(ARTIFACT_DIR, f"placement_model_v{version}_metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved model artifact: {model_path}")
    print(f"Saved metadata: placement_model_v{version}_metadata.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/placement_training.csv")
    args = parser.parse_args()
    train(args.data)
