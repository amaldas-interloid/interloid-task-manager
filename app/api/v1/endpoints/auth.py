from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    UserResponse,
)
from app.schemas.common import APIResponse
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> APIResponse[UserResponse]:
    service = AuthService(session)

    user = await service.register(request)

    return APIResponse(
        success=True,
        message="User registered successfully",
        data=user,
        error=None,
    )


@router.post(
    "/login",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> APIResponse[LoginResponse]:
    service = AuthService(session)

    tokens = await service.login(request)

    return APIResponse(
        success=True,
        message="Login successful",
        data=tokens,
        error=None,
    )


@router.post(
    "/refresh",
    response_model=APIResponse[LoginResponse],
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> APIResponse[LoginResponse]:
    service = AuthService(session)

    tokens = await service.refresh_access_token(request.refresh_token)

    return APIResponse(
        success=True,
        message="Access token refreshed successfully",
        data=tokens,
        error=None,
    )


@router.post(
    "/logout",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: RefreshRequest,
    session: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    service = AuthService(session)

    await service.logout(
        request.refresh_token,
    )

    return APIResponse(
        success=True,
        message="Logged out successfully",
        data=None,
        error=None,
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserResponse]:
    user = UserResponse.model_validate(current_user)
    return APIResponse(
        success=True,
        message="Current user retrieved successfully",
        data=user,
        error=None,
    )


@router.patch(
    "/change-password",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    service = AuthService(session)
    await service.change_password(
        current_user,
        request,
    )

    return APIResponse(
        success=True, message="password changed successfully", data=None, error=None
    )
