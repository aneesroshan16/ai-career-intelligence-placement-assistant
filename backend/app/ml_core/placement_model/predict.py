"""
Inference path for the placement prediction model. Pure function of
(features) -> (probability, label) — kept framework-agnostic so it's easily
unit-testable without spinning up FastAPI or a DB.
"""
from __future__ import annotations

import pandas as pd

from app.ml_core.placement_model.features import PlacementFeatures
from app.ml_core.placement_model.registry import LoadedModel, get_active_model


def predict_placement(features: PlacementFeatures, loaded_model: LoadedModel | None = None) -> dict:
    loaded_model = loaded_model or get_active_model()
    row = pd.DataFrame([features.to_vector()], columns=loaded_model.feature_order)

    model = loaded_model.model
    probability = float(model.predict_proba(row)[0][1])

    return {
        "probability": round(probability, 4),
        "predicted_label": probability >= 0.5,
        "model_version": f"{loaded_model.model_type}_v{loaded_model.version}",
    }
