from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def get_or_create_from_claims(self, user_id: str, email: str) -> User:
        """
        Called from core.security.get_current_user on every authenticated
        request. Since Supabase Auth owns identity, the backend never has an
        explicit "signup" step — the first authenticated request for a given
        Supabase user id provisions the local `users` + `student_profiles` rows.
        """
        user = await self.repo.get_by_id(user_id)
        if user is None:
            user = await self.repo.create(user_id=user_id, email=email)
        return user

    async def update_profile(self, user_id: str, **fields):
        return await self.repo.update_profile(user_id, **fields)

    async def get_profile(self, user_id: str) -> User | None:
        return await self.repo.get_by_id(user_id)
