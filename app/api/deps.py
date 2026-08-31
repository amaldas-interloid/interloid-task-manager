from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.dependencies import get_db
from app.enums.role import RoleName
from app.enums.token import TokenType
from app.exceptions.auth import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedException()

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise UnauthorizedException() from exc

    if payload.get("type") != TokenType.ACCESS.value:
        raise UnauthorizedException()

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise UnauthorizedException()

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise UnauthorizedException() from exc

    user_repository = UserRepository(session)

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedException()

    if not user.is_active:
        raise UnauthorizedException()

    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != RoleName.ADMIN:
        raise ForbiddenException()

    return current_user
