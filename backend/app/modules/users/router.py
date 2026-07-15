from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.middleware import success_envelope
from app.core.security import AuthenticatedUser, get_current_user, require_role
from app.modules.users.schemas import ProfileUpdateIn, UserOut
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_me(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    db_user = await service.get_profile(user.id)
    if db_user is None:
        raise NotFoundError("User not found")
    return success_envelope(UserOut.model_validate(db_user), request)


@router.put("/me")
async def update_me(
    payload: ProfileUpdateIn,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    if payload.full_name is not None:
        db_user = await service.get_profile(user.id)
        db_user.full_name = payload.full_name
        await db.commit()
    await service.update_profile(user.id, **payload.model_dump(exclude={"full_name"}, exclude_unset=True))
    db_user = await service.get_profile(user.id)
    return success_envelope(UserOut.model_validate(db_user), request)


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    request: Request,
    _: AuthenticatedUser = Depends(require_role(["admin", "placement_officer"])),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    db_user = await service.get_profile(user_id)
    if db_user is None:
        raise NotFoundError("User not found")
    return success_envelope(UserOut.model_validate(db_user), request)
