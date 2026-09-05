from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, RefreshToken)

    async def get_by_token_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
            )
            .with_for_update()
        )

        return result.scalar_one_or_none()

    async def revoke(
        self,
        refresh_token: RefreshToken,
    ) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        await self.session.flush()

    async def revoke_all_for_user(
        self,
        id: UUID,
    ) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == id)
            .values(revoked_at=datetime.now(UTC))
        )

        await self.session.flush()
