from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.dependencies import get_db
from app.enums.role import RoleName
from app.exceptions.auth import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.repositories.user import UserRepository

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise UnauthorizedException(
            message="Invalid or expired access token",
            code="INVALID_ACCESS_TOKEN",
        ) from exc

    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise UnauthorizedException(
            message="Invalid access token",
            code="INVALID_ACCESS_TOKEN",
        )

    try:
        user_id = UUID(subject)
    except ValueError as exc:
        raise UnauthorizedException(
            message="Invalid access token",
            code="INVALID_ACCESS_TOKEN",
        ) from exc

    user_repository = UserRepository(session)

    user = await user_repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedException(
            message="Invalid access token",
            code="INVALID_ACCESS_TOKEN",
        )

    if not user.is_active:
        raise UnauthorizedException(
            message="User account is inactive",
            code="USER_INACTIVE",
        )

    return user

async def require_admin(
        current_user: User =Depends(get_current_user),
) -> User:

    if  current_user.role != RoleName.ADMIN:
        raise ForbiddenException()

    return current_user