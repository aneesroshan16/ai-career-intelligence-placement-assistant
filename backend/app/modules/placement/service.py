import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ml_core.placement_model.features import PlacementFeatures
from app.ml_core.placement_model.predict import predict_placement
from app.modules.placement.repository import PlacementRepository


class PlacementService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PlacementRepository(session)

    async def predict(self, user_id: str, features: PlacementFeatures) -> dict:
        result = predict_placement(features)
        await self.repo.create(
            user_id=uuid.UUID(user_id),
            model_version=result["model_version"],
            input_features=features.model_dump(),
            probability=result["probability"],
            predicted_label=result["predicted_label"],
        )
        return result

    async def history(self, user_id: str):
        return await self.repo.history(user_id)
