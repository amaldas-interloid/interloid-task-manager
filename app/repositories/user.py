from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def email_exists(
        self,
        email: str,
    ) -> bool:
        return await self.get_by_email(email) is not None

    async def get_with_role(
        self,
        user_id: UUID,
    ) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )

        return result.scalar_one_or_none()
