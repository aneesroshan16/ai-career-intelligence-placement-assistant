from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user
from app.ml_core.placement_model.features import PlacementFeatures
from app.modules.placement.schemas import PlacementPredictIn, PlacementPredictionOut, PlacementPredictOut
from app.modules.placement.service import PlacementService

router = APIRouter(prefix="/placement", tags=["Placement Prediction"])


@router.post("/predict")
async def predict_placement_probability(
    payload: PlacementPredictIn,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PlacementService(db)
    features = PlacementFeatures(**payload.model_dump())
    result = await service.predict(user.id, features)
    return success_envelope(PlacementPredictOut(**result), request)


@router.get("/predict/history")
async def get_prediction_history(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PlacementService(db)
    history = await service.history(user.id)
    return success_envelope([PlacementPredictionOut.model_validate(p) for p in history], request)
