from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email),
        )

        return result.scalar_one_or_none()

    async def email_exists(
        self,
        email: str,
    ) -> bool:
        return await self.get_by_email(email) is not None

    async def create(
        self,
        user: User,
    ) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        return user

    async def update_password(
            self,
            user: User,
            password_hash: str,
    ) -> User:
        user.password_hash = password_hash

        await self.session.flush()
        await self.session.refresh(user)

        return user
    
