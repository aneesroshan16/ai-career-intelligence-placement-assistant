import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.users.models import StudentProfile, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == uuid.UUID(user_id)).options(selectinload(User.profile))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: str, email: str, full_name: str = "") -> User:
        user = User(id=uuid.UUID(user_id), email=email, full_name=full_name or email.split("@")[0])
        self.session.add(user)
        profile = StudentProfile(user_id=user.id)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(user, attribute_names=["profile"])
        return user

    async def update_profile(self, user_id: str, **fields) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.user_id == uuid.UUID(user_id))
        result = await self.session.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile is None:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def list_by_department(self, department_id: int) -> list[User]:
        stmt = (
            select(User)
            .join(StudentProfile)
            .where(StudentProfile.department_id == department_id)
            .options(selectinload(User.profile))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
