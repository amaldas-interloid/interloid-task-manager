from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.exceptions.auth import (
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    InvalidCurrentPasswordException,
    InvalidRefreshTokenException,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.user_repository = UserRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)

    async def register(
        self,
        request: RegisterRequest,
    ) -> UserResponse:

        if await self.user_repository.email_exists(request.email):
            raise EmailAlreadyExistsException()

        hashed_password = hash_password(request.password)

        user = User(
            email=request.email,
            password_hash=hashed_password,
            first_name=request.first_name,
            last_name=request.last_name,
        )

        user = await self.user_repository.create(user)

        return UserResponse.model_validate(user)

    async def login(
        self,
        request: LoginRequest,
    ) -> LoginResponse:
        user = await self.user_repository.get_by_email(request.email)

        password_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH

        password_ok = verify_password(request.password, password_hash)

        if user is None or not password_ok or not user.is_active:
            raise InvalidCredentialsException()

        access_token = create_access_token(
            subject=str(user.id),
        )

        refresh_token = create_refresh_token()

        refresh_token_hash = hash_refresh_token(refresh_token)

        refresh_token_record = RefreshToken(
            token_hash=refresh_token_hash,
            expires_at=datetime.now(UTC)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            user_id=user.id,
        )
        await self.refresh_token_repository.create(
            refresh_token_record,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> LoginResponse:
        refresh_token_hash = hash_refresh_token(refresh_token)

        stored_token = await self.refresh_token_repository.get_by_token_hash(
            refresh_token_hash
        )
        if stored_token is None:
            raise InvalidRefreshTokenException()

        if stored_token.revoked_at is not None:
            raise InvalidRefreshTokenException()

        if stored_token.expires_at <= datetime.now(UTC):
            raise InvalidRefreshTokenException()

        user = await self.user_repository.get_by_id(
            stored_token.user_id,
        )

        if user is None or not user.is_active:
            raise InvalidRefreshTokenException()

        await self.refresh_token_repository.revoke(
            stored_token,
        )

        new_refresh_token = create_refresh_token()

        new_refresh_token_hash = hash_refresh_token(
            new_refresh_token,
        )

        new_refresh_token_record = RefreshToken(
            token_hash=new_refresh_token_hash,
            expires_at=(
                datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            ),
            user_id=user.id,
        )

        await self.refresh_token_repository.create(
            new_refresh_token_record,
        )

        access_token = create_access_token(
            subject=str(user.id),
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

    async def logout(
        self,
        refresh_token: str,
    ) -> None:
        refresh_token_hash = hash_refresh_token(refresh_token)

        stored_token = await self.refresh_token_repository.get_by_token_hash(
            refresh_token_hash,
        )

        if stored_token is None:
            raise InvalidRefreshTokenException()

        if stored_token.revoked_at is not None:
            return

        await self.refresh_token_repository.revoke(
            stored_token,
        )

    async def change_password(
        self,
        user: User,
        request: ChangePasswordRequest,
    ) -> None:
        if not verify_password(
            request.current_password,
            user.password_hash,
        ):
            raise InvalidCurrentPasswordException()

        new_password_hash = hash_password(
            request.new_password,
        )

        await self.user_repository.update_password(
            user,
            new_password_hash,
        )

        await self.refresh_token_repository.revoke_all_for_user(
            user.id,
        )
