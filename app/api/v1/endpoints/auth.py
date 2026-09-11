from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_session_id, get_current_user
from app.api.responses import (
    EMAIL_ALREADY_EXISTS_RESPONSE,
    INVALID_CREDENTIALS_RESPONSE,
    INVALID_CURRENT_PASSWORD_RESPONSE,
    INVALID_REFRESH_TOKEN_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas import (
    APIResponse,
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    SessionListResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        **EMAIL_ALREADY_EXISTS_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db, scope="function"),
) -> APIResponse[UserResponse]:
    service = AuthService(session)

    user = await service.register(request)

    return APIResponse(
        message="User registered successfully",
        data=user,
    )


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **INVALID_CREDENTIALS_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def login(
    request: LoginRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_db, scope="function"),
) -> APIResponse[LoginResponse]:
    service = AuthService(session)

    user_agent = http_request.headers.get(
        "user-agent",
    )

    client_ip = (
        http_request.client.host if http_request.client is not None else "unknown"
    )

    tokens = await service.login(
        request,
        user_agent=user_agent,
        client_ip=client_ip,
    )

    return APIResponse(
        message="Login successful",
        data=tokens,
    )


@router.post(
    "/refresh",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **INVALID_REFRESH_TOKEN_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db, scope="function"),
) -> APIResponse[LoginResponse]:
    service = AuthService(session)

    tokens = await service.refresh_access_token(request.refresh_token)

    return APIResponse(
        message="Access token refreshed successfully",
        data=tokens,
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def logout(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db, scope="function"),
) -> APIResponse[None]:
    service = AuthService(session)

    await service.logout(
        request.refresh_token,
    )

    return APIResponse(
        message="Logged out successfully",
    )


@router.post(
    "/logout-all",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def logout_all(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db, scope="function"),
    ],
) -> APIResponse[None]:
    service = AuthService(session)

    await service.logout_all(
        current_user,
    )

    return APIResponse(
        message="logged out from all sessions successfully",
        data=None,
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    user = UserResponse.model_validate(current_user)
    return APIResponse(
        message="Current user retrieved successfully",
        data=user,
    )


@router.patch(
    "/change-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        **INVALID_CURRENT_PASSWORD_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db, scope="function"),
) -> APIResponse[None]:
    service = AuthService(session)
    await service.change_password(
        current_user,
        request,
    )

    return APIResponse(
        message="password changed successfully",
    )


@router.get(
    "/sessions",
    response_model=APIResponse[SessionListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def get_sessions(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    current_session_id: Annotated[
        UUID,
        Depends(get_current_session_id),
    ],
    session: Annotated[
        AsyncSession,
        Depends(get_db, scope="function"),
    ],
) -> APIResponse[SessionListResponse]:
    service = AuthService(session)

    result = await service.get_sessions(
        user=current_user,
        current_session_id=current_session_id,
    )

    return APIResponse(
        message="Active sessions fetched successfully",
        data=result,
    )


@router.delete(
    "/sessions/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
    },
)
async def revoke_session(
    id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db, scope="function")],
) -> APIResponse[None]:
    service = AuthService(session)

    await service.revoke_session(
        user=current_user,
        family_id=id,
    )

    return APIResponse(
        message="session revoked successfully",
        data=None,
    )
