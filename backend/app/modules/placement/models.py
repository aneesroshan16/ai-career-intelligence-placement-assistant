import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PlacementPrediction(Base):
    __tablename__ = "placement_predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    input_features: Mapped[dict] = mapped_column(JSONB, nullable=False)
    probability: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    predicted_label: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
