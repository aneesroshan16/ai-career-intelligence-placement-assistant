"""
Model registry: discovers the highest-version trained artifact in
ml_core/artifacts/, loads it once at first use, and caches it in memory for
the lifetime of the process. `placement.service.py` depends on
`get_active_model()` only — it never touches the filesystem or a specific
model class directly.
"""
from __future__ import annotations

import glob
import json
import os
import pickle
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.core.exceptions import ModelNotFoundError

ARTIFACT_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")


@dataclass
class LoadedModel:
    model: Any
    model_type: str
    version: int
    feature_order: list[str]
    metrics: dict


def _latest_metadata_path() -> str | None:
    paths = glob.glob(os.path.join(ARTIFACT_DIR, "placement_model_v*_metadata.json"))
    if not paths:
        return None

    def version_of(p: str) -> int:
        try:
            return int(os.path.basename(p).split("_v")[1].split("_")[0])
        except (IndexError, ValueError):
            return 0

    return max(paths, key=version_of)


def _load_model_file(metadata: dict):
    model_path = os.path.join(ARTIFACT_DIR, metadata["model_filename"])
    if metadata["model_type"] == "catboost":
        from catboost import CatBoostClassifier

        model = CatBoostClassifier()
        model.load_model(model_path)
        return model
    with open(model_path, "rb") as f:
        return pickle.load(f)


@lru_cache
def get_active_model() -> LoadedModel:
    metadata_path = _latest_metadata_path()
    if metadata_path is None:
        raise ModelNotFoundError(
            "No trained placement model found. Run "
            "`python -m app.ml_core.placement_model.train --data data/placement_training.csv` first."
        )
    with open(metadata_path) as f:
        metadata = json.load(f)

    model = _load_model_file(metadata)
    return LoadedModel(
        model=model,
        model_type=metadata["model_type"],
        version=metadata["version"],
        feature_order=metadata["feature_order"],
        metrics=metadata.get("selected_metrics", {}),
    )


def reload_active_model() -> LoadedModel:
    """Clears the cache and reloads — call after training a new version."""
    get_active_model.cache_clear()
    return get_active_model()
